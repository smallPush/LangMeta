import pytest
import benchmark_sanitize
import subprocess
import sys

def test_original_sanitizer():
    access_token = "secret!token"
    sanitizer = benchmark_sanitize.OriginalSanitizer(access_token)

    # Empty string
    assert sanitizer._sanitize_string("") == ""
    assert sanitizer._sanitize_string(None) is None

    # Regular string without token
    assert sanitizer._sanitize_string("No token here") == "No token here"

    # String with raw token
    assert sanitizer._sanitize_string("Error with secret!token") == "Error with ***"

    # String with encoded token (quote)
    assert sanitizer._sanitize_string("Error with secret%21token") == "Error with ***"

    # String with both
    assert sanitizer._sanitize_string("Error: secret!token encoded: secret%21token") == "Error: *** encoded: ***"

def test_optimized_sanitizer():
    access_token = "secret!token"
    sanitizer = benchmark_sanitize.OptimizedSanitizer(access_token)

    # Empty string
    assert sanitizer._sanitize_string("") == ""
    assert sanitizer._sanitize_string(None) is None

    # Regular string without token
    assert sanitizer._sanitize_string("No token here") == "No token here"

    # String with raw token
    assert sanitizer._sanitize_string("Error with secret!token") == "Error with ***"

    # String with encoded token (quote)
    assert sanitizer._sanitize_string("Error with secret%21token") == "Error with ***"

    # String with both
    assert sanitizer._sanitize_string("Error: secret!token encoded: secret%21token") == "Error: *** encoded: ***"

def test_run_benchmark(capsys):
    benchmark_sanitize.run_benchmark()

    captured = capsys.readouterr()
    assert "Original:" in captured.out
    assert "Optimized:" in captured.out
    assert "Improvement:" in captured.out
    assert "faster" in captured.out

def test_benchmark_sanitize_main_execution():
    result = subprocess.run([sys.executable, "benchmark_sanitize.py"], capture_output=True, text=True)

    assert result.returncode == 0
    assert "Original:" in result.stdout
    assert "Optimized:" in result.stdout
    assert "Improvement:" in result.stdout
    assert "faster" in result.stdout
