#!/usr/bin/env python3
"""
Quick test script to verify adaptive concurrency limiter works correctly.
This script tests the fix without running a full OMNI project generation.
"""

import asyncio
import psutil
from swarm import SwarmAgent


def test_concurrency_calculation():
    """Test that concurrency is calculated based on available RAM."""
    print("=" * 70)
    print("TESTING ADAPTIVE CONCURRENCY LIMITER")
    print("=" * 70)
    print()

    # Check system memory
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024 ** 3)
    print(f"System Memory Status:")
    print(f"  Available RAM: {available_gb:.2f} GB")
    print(f"  Memory Usage: {mem.percent:.1f}%")
    print()

    # Create SwarmAgent and check concurrency
    print("Creating SwarmAgent...")
    agent = SwarmAgent()
    print()

    print(f"✅ SwarmAgent Configuration:")
    print(f"  Max Concurrent Tasks: {agent.max_concurrent_tasks}")
    print(f"  Semaphore Value: {agent.semaphore._value}")
    print()

    # Verify logic
    expected = None
    if available_gb < 2:
        expected = 1
    elif available_gb < 4:
        expected = 2
    elif available_gb < 6:
        expected = 4
    elif available_gb < 8:
        expected = 6
    else:
        expected = min(8, int(available_gb / 1.5))

    print(f"Expected Concurrency: {expected}")
    print(f"Actual Concurrency: {agent.max_concurrent_tasks}")
    print()

    if agent.max_concurrent_tasks == expected:
        print("✅ PASS: Concurrency calculation correct!")
    else:
        print(f"⚠️  WARNING: Expected {expected} but got {agent.max_concurrent_tasks}")
        print("   (This might be OK if ENV variable is set)")
    print()

    # Test with different memory scenarios
    print("-" * 70)
    print("Testing with simulated memory scenarios:")
    print()

    scenarios = [
        (1.5, 1, "Low memory (safe mode)"),
        (3.5, 2, "Medium memory"),
        (5.5, 4, "High memory"),
        (10.0, 6, "Very high memory"),
    ]

    from unittest.mock import patch

    for ram_gb, expected_tasks, description in scenarios:
        with patch('psutil.virtual_memory') as mock_vm:
            mock_vm.return_value.available = ram_gb * 1024 ** 3
            mock_vm.return_value.percent = 50
            
            test_agent = SwarmAgent()
            status = "✅" if test_agent.max_concurrent_tasks == expected_tasks else "❌"
            print(f"  {status} {description} ({ram_gb}GB RAM) → {test_agent.max_concurrent_tasks} tasks")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


async def test_semaphore_limiting():
    """Test that semaphore actually limits concurrent execution."""
    print()
    print("=" * 70)
    print("TESTING SEMAPHORE LIMITING")
    print("=" * 70)
    print()

    from unittest.mock import patch

    # Create agent with limited concurrency
    with patch('psutil.virtual_memory') as mock_vm:
        mock_vm.return_value.available = 4 * 1024 ** 3
        mock_vm.return_value.percent = 50
        agent = SwarmAgent()

    print(f"Agent concurrency limit: {agent.max_concurrent_tasks}")
    print()

    # Track concurrent execution
    max_concurrent = [0]
    current = [0]

    async def mock_task(task_id):
        """Simulate a task with semaphore."""
        async with agent.semaphore:
            current[0] += 1
            if current[0] > max_concurrent[0]:
                max_concurrent[0] = current[0]
            
            print(f"  Task {task_id} running (current: {current[0]})")
            await asyncio.sleep(0.1)  # Simulate work
            current[0] -= 1

    print("Launching 10 tasks (should limit to concurrency setting)...")
    print()

    tasks = [mock_task(i) for i in range(10)]
    await asyncio.gather(*tasks)

    print()
    print(f"Results:")
    print(f"  Max concurrent tasks observed: {max_concurrent[0]}")
    print(f"  Expected limit: {agent.max_concurrent_tasks}")
    
    if max_concurrent[0] <= agent.max_concurrent_tasks:
        print(f"  ✅ PASS: Semaphore correctly limited concurrency!")
    else:
        print(f"  ❌ FAIL: Exceeded concurrency limit!")

    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    # Run tests
    test_concurrency_calculation()
    asyncio.run(test_semaphore_limiting())
    
    print("🎉 All manual tests complete!")
    print()
    print("Next steps:")
    print("  1. Run full test suite: pytest tests/unit/test_swarm_concurrency.py")
    print("  2. Test with actual project: python main.py create \"test project\"")
    print("  3. Monitor memory usage during execution")
