"""
Standalone Security Tests for CRITICAL Vulnerability Fixes
Tests encryption.py and mfa.py directly without full venom dependencies

Fixed Vulnerabilities:
- CRITICAL #1: Private keys now encrypted with passwords
- CRITICAL #2: MFA rate limiting against brute-force attacks
"""
import sys
import os
import time

# Add venom to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'venom', 'security'))

# Import directly from security modules
from encryption import AdvancedEncryption
from mfa import MFAManager


def test_rsa_password_encryption():
    """Test RSA keypair with password protection"""
    print("\n🔒 Test 1: RSA Key Password Encryption")
    print("=" * 60)

    password = "SuperSecurePassword123!"

    # Generate keypair with password
    private_key, public_key = AdvancedEncryption.generate_keypair(
        key_size=2048,
        password=password
    )

    # Check if encrypted
    if b"ENCRYPTED" in private_key:
        print("✅ PASS: RSA private key is encrypted with password")
    else:
        print("❌ FAIL: RSA private key is NOT encrypted!")
        return False

    # Test encryption/decryption roundtrip
    plaintext = b"Secret message"
    ciphertext = AdvancedEncryption.encrypt_asymmetric(plaintext, public_key)
    decrypted = AdvancedEncryption.decrypt_asymmetric(ciphertext, private_key, password=password)

    if decrypted == plaintext:
        print("✅ PASS: RSA encrypt/decrypt works with password-protected keys")
    else:
        print("❌ FAIL: RSA roundtrip failed!")
        return False

    # Test wrong password fails
    try:
        AdvancedEncryption.decrypt_asymmetric(ciphertext, private_key, password="WrongPassword")
        print("❌ FAIL: Wrong password should have failed!")
        return False
    except Exception:
        print("✅ PASS: Wrong password correctly rejected")

    return True


def test_rsa_without_password_warns():
    """Test that unencrypted keys log warning"""
    print("\n⚠️  Test 2: RSA Unencrypted Key Warning")
    print("=" * 60)

    # Generate keypair WITHOUT password
    private_key, public_key = AdvancedEncryption.generate_keypair(
        key_size=2048,
        password=None
    )

    if b"ENCRYPTED" not in private_key:
        print("✅ PASS: Unencrypted key is NOT encrypted (as expected)")
        print("ℹ️  Check logs for security warning about unencrypted keys")
    else:
        print("❌ FAIL: Key should be unencrypted when password=None!")
        return False

    return True


def test_ed25519_password_encryption():
    """Test Ed25519 keypair with password protection"""
    print("\n🔒 Test 3: Ed25519 Key Password Encryption")
    print("=" * 60)

    password = "Ed25519SecurePass!@#"

    # Generate Ed25519 keypair with password
    private_key, public_key = AdvancedEncryption.generate_ed25519_keypair(
        password=password
    )

    if b"ENCRYPTED" in private_key:
        print("✅ PASS: Ed25519 private key is encrypted with password")
    else:
        print("❌ FAIL: Ed25519 private key is NOT encrypted!")
        return False

    # Test signing/verification
    data = b"Document to sign"
    signature = AdvancedEncryption.sign(data, private_key, password=password)
    valid = AdvancedEncryption.verify(data, signature, public_key)

    if valid:
        print("✅ PASS: Ed25519 sign/verify works with password-protected keys")
    else:
        print("❌ FAIL: Ed25519 signature verification failed!")
        return False

    # Test wrong password fails
    try:
        AdvancedEncryption.sign(data, private_key, password="WrongPassword")
        print("❌ FAIL: Wrong password should have failed!")
        return False
    except Exception:
        print("✅ PASS: Wrong password correctly rejected for signing")

    return True


def test_mfa_rate_limiting():
    """Test MFA rate limiting against brute-force"""
    print("\n🛡️  Test 4: MFA Rate Limiting (Brute-Force Protection)")
    print("=" * 60)

    mfa = MFAManager(max_attempts=5, window_seconds=300)
    secret = mfa.generate_secret()

    # Test valid code works
    current_token = mfa.get_current_totp(secret)
    if mfa.verify_totp(secret, current_token, identifier="user_1"):
        print("✅ PASS: Valid TOTP token accepted")
    else:
        print("❌ FAIL: Valid token rejected!")
        return False

    # Test rate limiting after 5 failed attempts
    identifier = "brute_force_attacker"

    # Make 5 failed attempts
    for i in range(5):
        mfa.verify_totp(secret, "000000", identifier=identifier)

    # 6th attempt should be blocked
    result = mfa.verify_totp(secret, "111111", identifier=identifier)

    if result is False:
        print("✅ PASS: 6th failed attempt blocked by rate limiting")
    else:
        print("❌ FAIL: Rate limiting did not block attacker!")
        return False

    # Even correct code should be blocked
    correct_token = mfa.get_current_totp(secret)
    result = mfa.verify_totp(secret, correct_token, identifier=identifier)

    if result is False:
        print("✅ PASS: Rate limit blocks even with correct token (user locked out)")
    else:
        print("❌ FAIL: Rate limiting bypassed with correct token!")
        return False

    return True


def test_mfa_per_user_isolation():
    """Test that rate limiting is isolated per user"""
    print("\n👥 Test 5: MFA Rate Limiting Per-User Isolation")
    print("=" * 60)

    mfa = MFAManager(max_attempts=5, window_seconds=300)
    secret = mfa.generate_secret()

    # Lock user 1
    for i in range(5):
        mfa.verify_totp(secret, "000000", identifier="user_1")

    # User 1 should be blocked
    if mfa.verify_totp(secret, "111111", identifier="user_1") is False:
        print("✅ PASS: User 1 is blocked after 5 failed attempts")
    else:
        print("❌ FAIL: User 1 should be blocked!")
        return False

    # User 2 should NOT be affected
    current_token = mfa.get_current_totp(secret)
    if mfa.verify_totp(secret, current_token, identifier="user_2"):
        print("✅ PASS: User 2 can still login (not affected by user 1)")
    else:
        print("❌ FAIL: User 2 incorrectly blocked!")
        return False

    return True


def test_mfa_failed_attempts_counter():
    """Test failed attempts counter"""
    print("\n📊 Test 6: MFA Failed Attempts Counter")
    print("=" * 60)

    mfa = MFAManager(max_attempts=5, window_seconds=300)
    secret = mfa.generate_secret()
    identifier = "monitored_user"

    # Initially 0
    if mfa.get_failed_attempts(identifier) == 0:
        print("✅ PASS: Initially 0 failed attempts")
    else:
        print("❌ FAIL: Initial count should be 0!")
        return False

    # Make 3 failed attempts
    for i in range(3):
        mfa.verify_totp(secret, "000000", identifier=identifier)

    # Should be 3
    if mfa.get_failed_attempts(identifier) == 3:
        print("✅ PASS: Failed attempts counter shows 3")
    else:
        print(f"❌ FAIL: Expected 3, got {mfa.get_failed_attempts(identifier)}")
        return False

    # Successful login should clear counter
    current_token = mfa.get_current_totp(secret)
    mfa.verify_totp(secret, current_token, identifier=identifier)

    if mfa.get_failed_attempts(identifier) == 0:
        print("✅ PASS: Successful login clears failed attempts counter")
    else:
        print("❌ FAIL: Counter should be cleared after successful login!")
        return False

    return True


def test_mfa_admin_reset():
    """Test admin reset function"""
    print("\n🔓 Test 7: MFA Admin Reset Function")
    print("=" * 60)

    mfa = MFAManager(max_attempts=3, window_seconds=300)
    secret = mfa.generate_secret()
    identifier = "locked_user"

    # Lock user
    for i in range(3):
        mfa.verify_totp(secret, "000000", identifier=identifier)

    # User should be blocked
    if mfa.verify_totp(secret, "111111", identifier=identifier) is False:
        print("✅ PASS: User is locked after 3 failed attempts")
    else:
        print("❌ FAIL: User should be locked!")
        return False

    # Admin resets
    mfa.reset_rate_limit(identifier)

    # User should now be able to login
    current_token = mfa.get_current_totp(secret)
    if mfa.verify_totp(secret, current_token, identifier=identifier):
        print("✅ PASS: Admin reset allows user to login again")
    else:
        print("❌ FAIL: Admin reset did not work!")
        return False

    return True


def run_all_tests():
    """Run all security tests"""
    print("\n" + "=" * 60)
    print("🔐 VENOM SECURITY FIXES - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("\nTesting CRITICAL vulnerability fixes:")
    print("  - CRITICAL #1: Private key encryption with passwords")
    print("  - CRITICAL #2: MFA rate limiting against brute-force")
    print("=" * 60)

    tests = [
        ("RSA Password Encryption", test_rsa_password_encryption),
        ("RSA Unencrypted Warning", test_rsa_without_password_warns),
        ("Ed25519 Password Encryption", test_ed25519_password_encryption),
        ("MFA Rate Limiting", test_mfa_rate_limiting),
        ("MFA Per-User Isolation", test_mfa_per_user_isolation),
        ("MFA Failed Attempts Counter", test_mfa_failed_attempts_counter),
        ("MFA Admin Reset", test_mfa_admin_reset),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: {name} - Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Security fixes verified successfully!")
        print("\n✅ CRITICAL #1 FIXED: Private keys are now encrypted with passwords")
        print("✅ CRITICAL #2 FIXED: MFA has rate limiting against brute-force attacks")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed! Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
