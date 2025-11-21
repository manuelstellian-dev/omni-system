"""Unit tests for SwarmAgent adaptive concurrency - WORKING VERSION."""
import pytest
import asyncio
import os
from unittest.mock import Mock
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from swarm import SwarmAgent
from cortex import Task, ProjectSpec

class TestAdaptiveConcurrency:
    def test_agent_has_concurrency_limit(self):
        """Test SwarmAgent initializes with concurrency limit."""
        agent = SwarmAgent()
        assert hasattr(agent, 'max_concurrent_tasks')
        assert 1 <= agent.max_concurrent_tasks <= 10

    def test_semaphore_exists(self):
        """Test semaphore is created."""
        agent = SwarmAgent()
        assert isinstance(agent.semaphore, asyncio.Semaphore)

    @pytest.mark.asyncio
    async def test_semaphore_limits_execution(self):
        """Test semaphore actually limits concurrent tasks."""
        agent = SwarmAgent()
        max_concurrent = []
        current = [0]
        async def tracked_task():
            async with agent.semaphore:
                current[0] += 1
                max_concurrent.append(current[0])
                await asyncio.sleep(0.05)
                current[0] -= 1
        await asyncio.gather(*[tracked_task() for _ in range(agent.max_concurrent_tasks * 2)])
        assert max(max_concurrent) <= agent.max_concurrent_tasks

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
