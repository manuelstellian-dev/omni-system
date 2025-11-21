"""
Adaptive Resource Management System for OMNI
Prevents system crashes by monitoring RAM/CPU and adjusting concurrency dynamically.
"""

import psutil
import asyncio
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """System resource thresholds"""
    max_ram_percent: float = 80.0  # REDUCED: 85 → 80 (more aggressive)  # Stop at 85% RAM
    max_cpu_percent: float = 85.0  # REDUCED: 90 → 85 (more aggressive)  # Stop at 90% CPU
    min_workers: int = 1
    max_workers: int = 3           # REDUCED: 8 → 3 (prevent RAM spike)
    check_interval: float = 2.0  # Check every 2 seconds


class AdaptiveConcurrency:
    """
    Monitors system resources and adjusts worker count dynamically.
    Prevents RAM/CPU overload that causes system crashes.
    """

    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self.current_workers = self.limits.max_workers
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None

    def get_system_resources(self) -> dict:
        """Get current system resource usage"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0)
            
            return {
                'ram_percent': memory.percent,
                'ram_available_gb': memory.available / (1024**3),
                'cpu_percent': cpu,
                'recommended_workers': self.current_workers
            }
        except Exception as e:
            logger.error(f"Failed to get system resources: {e}")
            return {
                'ram_percent': 0.0,
                'ram_available_gb': 0.0,
                'cpu_percent': 0.0,
                'recommended_workers': self.limits.min_workers
            }

    def should_reduce_load(self) -> bool:
        """Check if we need to reduce system load"""
        resources = self.get_system_resources()
        
        if resources['ram_percent'] > self.limits.max_ram_percent:
            logger.warning(f"⚠️  RAM at {resources['ram_percent']:.1f}% - Reducing load!")
            return True
            
        if resources['cpu_percent'] > self.limits.max_cpu_percent:
            logger.warning(f"⚠️  CPU at {resources['cpu_percent']:.1f}% - Reducing load!")
            return True
            
        return False

    def adjust_workers(self) -> int:
        """Dynamically adjust worker count based on resources"""
        resources = self.get_system_resources()
        ram = resources['ram_percent']
        cpu = resources['cpu_percent']
        
        # Critical: reduce immediately
        if ram > self.limits.max_ram_percent or cpu > self.limits.max_cpu_percent:
            self.current_workers = max(self.limits.min_workers, self.current_workers - 2)
            logger.warning(f"🔴 CRITICAL: Reduced workers to {self.current_workers}")
            
        # High: reduce gradually
        elif ram > 75 or cpu > 80:
            self.current_workers = max(self.limits.min_workers, self.current_workers - 1)
            logger.info(f"🟡 HIGH: Reduced workers to {self.current_workers}")
            
        # Normal: can increase
        elif ram < 60 and cpu < 60 and self.current_workers < self.limits.max_workers:
            self.current_workers = min(self.limits.max_workers, self.current_workers + 1)
            logger.info(f"🟢 NORMAL: Increased workers to {self.current_workers}")
            
        return self.current_workers

    async def start_monitoring(self):
        """Start background resource monitoring"""
        if self._monitoring:
            return
            
        self._monitoring = True
        logger.info("🔍 Starting adaptive resource monitoring...")
        
        while self._monitoring:
            try:
                self.adjust_workers()
                await asyncio.sleep(self.limits.check_interval)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)

    def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring = False
        logger.info("⏹️  Stopped resource monitoring")

    def get_safe_worker_count(self) -> int:
        """Get current safe worker count"""
        self.adjust_workers()  # Update before returning
        return self.current_workers


# Global singleton instance
_resource_manager: Optional[AdaptiveConcurrency] = None


def get_resource_manager() -> AdaptiveConcurrency:
    """Get or create global resource manager"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = AdaptiveConcurrency()
    return _resource_manager
