"""
Adaptive Resource Monitor for OMNI System
Monitors CPU, RAM, and adjusts concurrency dynamically
"""
import psutil
import time
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ResourceThresholds:
    """System resource thresholds"""
    cpu_critical: float = 90.0
    cpu_warning: float = 75.0
    memory_critical: float = 90.0
    memory_warning: float = 75.0
    min_concurrency: int = 1
    max_concurrency: int = 8
    default_concurrency: int = 4


class ResourceMonitor:
    """Monitors system resources and recommends concurrency levels"""
    
    def __init__(self, thresholds: Optional[ResourceThresholds] = None):
        self.thresholds = thresholds or ResourceThresholds()
        self.current_concurrency = self.thresholds.default_concurrency
        
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "cpu_count": psutil.cpu_count()
        }
    
    def calculate_safe_concurrency(self) -> int:
        """
        Calculate safe concurrency level based on current resources
        
        Logic:
        - CPU > 90% or RAM > 90% → concurrency = 1
        - CPU > 75% or RAM > 75% → concurrency = 2
        - CPU < 50% and RAM < 50% → concurrency = max (8)
        - Otherwise → concurrency = 4
        """
        metrics = self.get_system_metrics()
        cpu = metrics["cpu_percent"]
        memory = metrics["memory_percent"]
        
        # CRITICAL: Emergency mode
        if cpu >= self.thresholds.cpu_critical or memory >= self.thresholds.memory_critical:
            return self.thresholds.min_concurrency
        
        # WARNING: Reduced mode
        if cpu >= self.thresholds.cpu_warning or memory >= self.thresholds.memory_warning:
            return 2
        
        # OPTIMAL: High resources available
        if cpu < 50 and memory < 50:
            return self.thresholds.max_concurrency
        
        # DEFAULT: Normal operation
        return self.thresholds.default_concurrency
    
    def should_throttle(self) -> bool:
        """Check if system should throttle operations"""
        metrics = self.get_system_metrics()
        return (
            metrics["cpu_percent"] >= self.thresholds.cpu_critical or
            metrics["memory_percent"] >= self.thresholds.memory_critical
        )
    
    def get_recommendation(self) -> Dict:
        """Get resource status and recommendations"""
        metrics = self.get_system_metrics()
        safe_concurrency = self.calculate_safe_concurrency()
        
        status = "optimal"
        if metrics["cpu_percent"] >= self.thresholds.cpu_critical or \
           metrics["memory_percent"] >= self.thresholds.memory_critical:
            status = "critical"
        elif metrics["cpu_percent"] >= self.thresholds.cpu_warning or \
             metrics["memory_percent"] >= self.thresholds.memory_warning:
            status = "warning"
        
        return {
            "status": status,
            "metrics": metrics,
            "recommended_concurrency": safe_concurrency,
            "should_throttle": self.should_throttle(),
            "message": self._get_status_message(status, metrics)
        }
    
    def _get_status_message(self, status: str, metrics: Dict) -> str:
        """Generate human-readable status message"""
        if status == "critical":
            return f"⚠️  CRITICAL: CPU {metrics['cpu_percent']:.1f}% | RAM {metrics['memory_percent']:.1f}% - Emergency throttling"
        elif status == "warning":
            return f"⚠️  WARNING: CPU {metrics['cpu_percent']:.1f}% | RAM {metrics['memory_percent']:.1f}% - Reducing concurrency"
        else:
            return f"✓ OPTIMAL: CPU {metrics['cpu_percent']:.1f}% | RAM {metrics['memory_percent']:.1f}%"
    
    def adaptive_sleep(self, base_delay: float = 0.5) -> None:
        """Sleep adaptively based on system load"""
        if self.should_throttle():
            time.sleep(base_delay * 3)  # Triple delay under load
        elif self.get_system_metrics()["cpu_percent"] > 75:
            time.sleep(base_delay * 2)  # Double delay under warning
        else:
            time.sleep(base_delay)  # Normal delay
