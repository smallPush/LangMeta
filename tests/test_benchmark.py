import pytest
import asyncio
import benchmark
from unittest.mock import patch

@pytest.mark.asyncio
async def test_run_benchmark(capsys):
    # Call run_benchmark
    await benchmark.run_benchmark()

    # Read output
    captured = capsys.readouterr()

    # Assert benchmark prints execution time
    assert "Execution time:" in captured.out

    # We could also use capsys to check that it processed posts
    # "Running cron job to fetch posts, comments, and likes..."
    assert "Running cron job" in captured.out
    assert "Processing post: post_0" in captured.out

def test_benchmark_main_execution():
    import subprocess
    import sys
    # Run benchmark.py as a script
    result = subprocess.run([sys.executable, "benchmark.py"], capture_output=True, text=True)

    # Ensure subprocess exits cleanly
    assert result.returncode == 0
    assert "Execution time:" in result.stdout
    assert "Running cron job" in result.stdout
    assert "Processing post: post_0" in result.stdout
