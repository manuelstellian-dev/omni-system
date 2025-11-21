"""
Unit tests for SwarmAgent adaptive concurrency limiting.

Tests the memory-safe concurrency calculation and semaphore-based limiting
that prevents OOM crashes when executing large numbers of tasks in parallel.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


# Import the class to test
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from swarm import SwarmAgent
from cortex import Task, ProjectSpec


class TestAdaptiveConcurrency:
    """Test suite for adaptive concurrency calculation."""

    @patch("psutil.virtual_memory")
    def test_calculates_concurrency_for_low_memory_2gb(self, mock_vm):
        """Test that system uses 1 task when RAM < 2GB (safe mode)."""
        # Arrange: Simulate 1.5GB available RAM
        mock_vm.return_value.available = 1.5 * 1024**3  # 1.5GB in bytes
        mock_vm.return_value.percent = 75

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 1, "Should use 1 task for low memory"

    @patch("psutil.virtual_memory")
    def test_calculates_concurrency_for_medium_memory_4gb(self, mock_vm):
        """Test that system uses 2 tasks when RAM is 3-4GB."""
        # Arrange: Simulate 3.5GB available RAM
        mock_vm.return_value.available = 3.5 * 1024**3
        mock_vm.return_value.percent = 50

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 2, "Should use 2 tasks for medium memory"

    @patch("psutil.virtual_memory")
    def test_calculates_concurrency_for_high_memory_6gb(self, mock_vm):
        """Test that system uses 4 tasks when RAM is 5-6GB."""
        # Arrange: Simulate 5.5GB available RAM
        mock_vm.return_value.available = 5.5 * 1024**3
        mock_vm.return_value.percent = 40

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 4, "Should use 4 tasks for high memory"

    @patch("psutil.virtual_memory")
    def test_calculates_concurrency_for_very_high_memory_10gb(self, mock_vm):
        """Test that system caps at 8 tasks even with 10GB+ RAM."""
        # Arrange: Simulate 10GB available RAM
        mock_vm.return_value.available = 10 * 1024**3
        mock_vm.return_value.percent = 20

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks <= 8, "Should cap at 8 tasks maximum"
        assert agent.max_concurrent_tasks >= 6, "Should use 6-8 tasks for very high memory"

    @patch.dict(os.environ, {"OMNI_MAX_CONCURRENT_TASKS": "5"})
    @patch("psutil.virtual_memory")
    def test_respects_env_override_valid_number(self, mock_vm):
        """Test that ENV variable overrides automatic calculation."""
        # Arrange: Even with high RAM, use ENV override
        mock_vm.return_value.available = 8 * 1024**3
        mock_vm.return_value.percent = 30

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 5, "Should use ENV override value"

    @patch.dict(os.environ, {"OMNI_MAX_CONCURRENT_TASKS": "auto"})
    @patch("psutil.virtual_memory")
    def test_respects_env_auto_keyword(self, mock_vm):
        """Test that 'auto' keyword triggers automatic calculation."""
        # Arrange
        mock_vm.return_value.available = 4 * 1024**3
        mock_vm.return_value.percent = 50

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 2, "Should calculate automatically with 'auto'"

    @patch.dict(os.environ, {"OMNI_MAX_CONCURRENT_TASKS": "invalid"})
    @patch("psutil.virtual_memory")
    def test_handles_invalid_env_value_gracefully(self, mock_vm):
        """Test that invalid ENV value falls back to automatic calculation."""
        # Arrange
        mock_vm.return_value.available = 4 * 1024**3
        mock_vm.return_value.percent = 50

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 2, "Should fallback to auto calculation"

    @patch.dict(os.environ, {"OMNI_MAX_CONCURRENT_TASKS": "15"})
    @patch("psutil.virtual_memory")
    def test_rejects_env_value_out_of_range(self, mock_vm):
        """Test that ENV values >10 are rejected and fallback to auto."""
        # Arrange
        mock_vm.return_value.available = 6 * 1024**3
        mock_vm.return_value.percent = 40

        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 4, "Should reject >10 and use auto"

    @patch("psutil.virtual_memory", side_effect=Exception("psutil not available"))
    def test_fallback_when_psutil_fails(self, mock_vm):
        """Test that system falls back to safe default when psutil fails."""
        # Act
        agent = SwarmAgent()

        # Assert
        assert agent.max_concurrent_tasks == 3, "Should use safe default (3) on error"

    def test_semaphore_is_created_with_correct_limit(self):
        """Test that asyncio.Semaphore is created with calculated limit."""
        # Arrange & Act
        with patch("psutil.virtual_memory") as mock_vm:
            mock_vm.return_value.available = 6 * 1024**3
            mock_vm.return_value.percent = 40
            agent = SwarmAgent()

        # Assert
        assert isinstance(agent.semaphore, asyncio.Semaphore)
        assert agent.semaphore._value == 4, "Semaphore should have correct initial value"


class TestSemaphoreLimiting:
    """Test suite for semaphore-based concurrent task limiting."""

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrent_execution(self):
        """Test that semaphore actually limits number of concurrent tasks."""
        # Arrange
        max_concurrent = []  # Track max concurrent tasks
        current_count = [0]  # Track current executing tasks

        async def mock_task(task_id):
            """Mock task that tracks concurrency."""
            current_count[0] += 1
            max_concurrent.append(current_count[0])
            await asyncio.sleep(0.1)  # Simulate work
            current_count[0] -= 1

        with patch("psutil.virtual_memory") as mock_vm:
            mock_vm.return_value.available = 4 * 1024**3
            mock_vm.return_value.percent = 50
            agent = SwarmAgent()
            agent.max_concurrent_tasks = 2  # Force limit to 2 for testing
            agent.semaphore = asyncio.Semaphore(2)

        # Act: Execute 5 tasks that should be limited to 2 concurrent
        tasks = [mock_task(i) for i in range(5)]

        async def execute_with_semaphore(task_id):
            async with agent.semaphore:
                await mock_task(task_id)

        await asyncio.gather(*[execute_with_semaphore(i) for i in range(5)])

        # Assert
        assert max(max_concurrent) <= 2, "Should never exceed 2 concurrent tasks"

    @pytest.mark.asyncio
    async def test_execute_task_with_safety_uses_semaphore(self):
        """Test that _execute_task_with_safety properly acquires semaphore."""
        # Arrange
        with patch("psutil.virtual_memory") as mock_vm:
            mock_vm.return_value.available = 6 * 1024**3
            mock_vm.return_value.percent = 40
            agent = SwarmAgent()

        mock_task = Mock(spec=Task)
        mock_task.task_id = "test_task"
        mock_task.task_description = "Test task"
        mock_task.output_files = ["test.py"]
        mock_task.depends_on = []

        mock_spec = Mock(spec=ProjectSpec)
        mock_spec.project_name = "test-project"
        mock_spec.tech_stack = ["python"]
        mock_spec.database_schema = ""
        mock_spec.core_features = []

        target_path = Path("/tmp/test")
        progress = Mock()

        # Mock the actual _execute_task to avoid real execution
        agent._execute_task = Mock(return_value=asyncio.coroutine(lambda: None)())

        # Act
        await agent._execute_task_with_safety(mock_task, mock_spec, target_path, progress)

        # Assert
        agent._execute_task.assert_called_once()


class TestMemoryMonitoring:
    """Test suite for memory monitoring during execution."""

    @pytest.mark.asyncio
    @patch("psutil.virtual_memory")
    @patch("asyncio.sleep", return_value=asyncio.coroutine(lambda: None)())
    async def test_pauses_when_memory_high(self, mock_sleep, mock_vm):
        """Test that execution pauses when memory usage >85%."""
        # Arrange
        mock_vm.return_value.available = 6 * 1024**3
        mock_vm.return_value.percent = 90  # High memory usage

        agent = SwarmAgent()

        mock_task = Mock(spec=Task)
        mock_task.task_id = "test_task"
        mock_spec = Mock(spec=ProjectSpec)
        target_path = Path("/tmp/test")
        progress = Mock()

        agent._execute_task = Mock(return_value=asyncio.coroutine(lambda: None)())

        # Act
        await agent._execute_task_with_safety(mock_task, mock_spec, target_path, progress)

        # Assert
        mock_sleep.assert_called_once_with(3)  # Should pause for 3 seconds

    @pytest.mark.asyncio
    @patch("psutil.virtual_memory")
    async def test_continues_when_memory_ok(self, mock_vm):
        """Test that execution continues normally when memory is OK."""
        # Arrange
        mock_vm.return_value.available = 6 * 1024**3
        mock_vm.return_value.percent = 50  # Normal memory usage

        agent = SwarmAgent()

        mock_task = Mock(spec=Task)
        mock_spec = Mock(spec=ProjectSpec)
        target_path = Path("/tmp/test")
        progress = Mock()

        agent._execute_task = Mock(return_value=asyncio.coroutine(lambda: None)())

        # Act
        await agent._execute_task_with_safety(mock_task, mock_spec, target_path, progress)

        # Assert
        agent._execute_task.assert_called_once()  # Should execute normally


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
