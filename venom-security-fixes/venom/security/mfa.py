"""
Multi-Factor Authentication Module for VENOM
Provides TOTP and backup codes for 2FA with rate limiting
"""
import pyotp
import qrcode
import secrets
import string
import logging
import bcrypt
import time
import hmac
from typing import List, Dict
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


class MFAManager:
    """
    Multi-factor authentication manager with rate limiting

    Features:
    - TOTP (Time-based One-Time Password) with rate limiting
    - Backup codes generation and verification
    - QR code generation for authenticator apps
    - Secure code hashing with bcrypt
    - Brute-force protection (5 attempts per 5 minutes)
    - Constant-time comparison for security
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        """
        Initialize MFA manager with rate limiting

        Args:
            max_attempts: Maximum failed attempts allowed in time window (default: 5)
            window_seconds: Time window in seconds (default: 300 = 5 minutes)
        """
        self._rate_limit: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        logger.info(
            f"MFA manager initialized with rate limiting: "
            f"{max_attempts} attempts per {window_seconds}s"
        )
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a random secret for TOTP
        
        Returns:
            Base32-encoded secret string
        """
        return pyotp.random_base32()
    
    @staticmethod
    def get_provisioning_uri(secret: str, username: str, issuer: str = 'VENOM') -> str:
        """
        Generate provisioning URI for QR code
        
        Args:
            secret: TOTP secret
            username: Username/email
            issuer: Service name (default: VENOM)
            
        Returns:
            Provisioning URI for QR code
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)
    
    def verify_totp(self, secret: str, token: str, identifier: str) -> bool:
        """
        Verify TOTP token with rate limiting and timing attack protection

        Args:
            secret: TOTP secret
            token: 6-digit token from authenticator app
            identifier: Unique identifier for rate limiting (user ID or IP address)

        Returns:
            True if token is valid, False otherwise

        Security Features:
            - Rate limiting: max 5 attempts per 5 minutes (configurable)
            - Constant-time comparison to prevent timing attacks
            - Logs suspicious activity (multiple failed attempts)
            - Thread-safe implementation

        Raises:
            No exceptions raised; returns False on errors
        """
        try:
            # Check rate limit (thread-safe)
            with self._lock:
                now = time.time()
                attempts = self._rate_limit[identifier]

                # Remove attempts older than the time window
                attempts = [t for t in attempts if now - t < self.window_seconds]

                # Check if rate limit exceeded
                if len(attempts) >= self.max_attempts:
                    logger.warning(
                        f"🚨 SECURITY ALERT: Rate limit exceeded for {identifier} "
                        f"({len(attempts)} attempts in {self.window_seconds}s)"
                    )
                    return False

                # Verify TOTP
                totp = pyotp.TOTP(secret)
                # Verify with time drift tolerance (±1 period = ±30s)
                valid = totp.verify(token, valid_window=1)

                if not valid:
                    # Record failed attempt
                    attempts.append(now)
                    self._rate_limit[identifier] = attempts
                    logger.warning(
                        f"Failed MFA attempt for {identifier} "
                        f"({len(attempts)}/{self.max_attempts} attempts)"
                    )
                else:
                    # Clear failed attempts on success
                    self._rate_limit[identifier] = []
                    logger.info(f"✓ Successful MFA verification for {identifier}")

                return valid

        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False

    def reset_rate_limit(self, identifier: str) -> None:
        """
        Reset rate limit for a specific identifier (admin function)

        Args:
            identifier: Identifier to reset (user ID or IP)
        """
        with self._lock:
            if identifier in self._rate_limit:
                del self._rate_limit[identifier]
                logger.info(f"Rate limit reset for {identifier}")

    def get_failed_attempts(self, identifier: str) -> int:
        """
        Get number of failed attempts for identifier in current window

        Args:
            identifier: Identifier to check (user ID or IP)

        Returns:
            Number of failed attempts in current time window
        """
        with self._lock:
            now = time.time()
            attempts = self._rate_limit.get(identifier, [])
            # Count only attempts within the time window
            recent_attempts = [t for t in attempts if now - t < self.window_seconds]
            return len(recent_attempts)
    
    @staticmethod
    def get_current_totp(secret: str) -> str:
        """
        Get current TOTP code
        
        Args:
            secret: TOTP secret
            
        Returns:
            Current 6-digit TOTP code
        """
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup codes
        
        Args:
            count: Number of backup codes to generate (default: 10)
            
        Returns:
            List of 8-character alphanumeric backup codes
            
        Note:
            Uses uppercase letters and digits (36 characters) for better
            readability and user experience. This provides sufficient entropy
            (8 chars from 36 = ~41 bits) for backup codes.
        """
        codes = []
        alphabet = string.ascii_uppercase + string.digits
        
        for _ in range(count):
            # Generate 8-character code
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            codes.append(code)
        
        logger.info(f"Generated {count} backup codes")
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        Hash backup code with bcrypt
        
        Args:
            code: Backup code to hash
            
        Returns:
            Hashed code (bcrypt hash string)
        """
        # Hash with bcrypt (includes salt)
        hashed = bcrypt.hashpw(code.encode(), bcrypt.gensalt())
        return hashed.decode()
    
    @staticmethod
    def verify_backup_code(code: str, hashed_codes: List[str]) -> bool:
        """
        Verify backup code against hashed codes
        
        Args:
            code: Backup code to verify
            hashed_codes: List of hashed backup codes
            
        Returns:
            True if code matches any hashed code, False otherwise
        """
        for hashed in hashed_codes:
            try:
                if bcrypt.checkpw(code.encode(), hashed.encode()):
                    logger.info("Backup code verified successfully")
                    return True
            except Exception as e:
                logger.warning(f"Backup code verification error: {e}")
                continue
        
        logger.warning("Backup code verification failed")
        return False
    
    @staticmethod
    def generate_qr_code(provisioning_uri: str, output_path: str) -> None:
        """
        Generate QR code image for TOTP provisioning
        
        Args:
            provisioning_uri: Provisioning URI from get_provisioning_uri()
            output_path: Path to save QR code image
        """
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            
            logger.info(f"QR code saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            raise
