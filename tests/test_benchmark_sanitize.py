import urllib.parse
import subprocess
import sys
import pytest
from benchmark_sanitize import OriginalSanitizer, OptimizedSanitizer, run_benchmark

@pytest.fixture
def access_token():
    return "secret_token_with_spaces and_chars/+"

@pytest.fixture
def orig_sanitizer(access_token):
    return OriginalSanitizer(access_token)

@pytest.fixture
def opt_sanitizer(access_token):
    return OptimizedSanitizer(access_token)

def test_original_sanitizer_normal(orig_sanitizer, access_token):
    text = f"This is a {access_token} test."
    assert orig_sanitizer._sanitize_string(text) == "This is a *** test."

def test_optimized_sanitizer_normal(opt_sanitizer, access_token):
    text = f"This is a {access_token} test."
    assert opt_sanitizer._sanitize_string(text) == "This is a *** test."

def test_original_sanitizer_encoded(orig_sanitizer, access_token):
    encoded = urllib.parse.quote(access_token)
    text = f"This is a {encoded} test."
    assert orig_sanitizer._sanitize_string(text) == "This is a *** test."

def test_optimized_sanitizer_encoded(opt_sanitizer, access_token):
    encoded = urllib.parse.quote(access_token)
    text = f"This is a {encoded} test."
    assert opt_sanitizer._sanitize_string(text) == "This is a *** test."

def test_original_sanitizer_encoded_plus(orig_sanitizer, access_token):
    encoded_plus = urllib.parse.quote_plus(access_token)
    text = f"This is a {encoded_plus} test."
    assert orig_sanitizer._sanitize_string(text) == "This is a *** test."

def test_optimized_sanitizer_encoded_plus(opt_sanitizer, access_token):
    encoded_plus = urllib.parse.quote_plus(access_token)
    text = f"This is a {encoded_plus} test."
    assert opt_sanitizer._sanitize_string(text) == "This is a *** test."

def test_original_sanitizer_edge_cases(orig_sanitizer):
    assert orig_sanitizer._sanitize_string("") == ""
    assert orig_sanitizer._sanitize_string(None) is None
    assert orig_sanitizer._sanitize_string("no token here") == "no token here"

def test_optimized_sanitizer_edge_cases(opt_sanitizer):
    assert opt_sanitizer._sanitize_string("") == ""
    assert opt_sanitizer._sanitize_string(None) is None
    assert opt_sanitizer._sanitize_string("no token here") == "no token here"

def test_optimized_sanitizer_manual_mutation(opt_sanitizer):
    new_token = "new_secret_token"
    opt_sanitizer.access_token = new_token
    # Need to manually update derived attributes as memory mentioned
    opt_sanitizer._encoded_token = urllib.parse.quote(new_token)
    opt_sanitizer._encoded_token_plus = urllib.parse.quote_plus(new_token)

    text = f"This is a {new_token} test."
    assert opt_sanitizer._sanitize_string(text) == "This is a *** test."

def test_run_benchmark_output(capsys):
    run_benchmark()
    captured = capsys.readouterr()
    assert "Original:" in captured.out
    assert "Optimized:" in captured.out
    assert "Improvement:" in captured.out
    assert "faster" in captured.out

def test_run_benchmark_subprocess():
    result = subprocess.run([sys.executable, "benchmark_sanitize.py"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Original:" in result.stdout
    assert "Optimized:" in result.stdout
    assert "Improvement:" in result.stdout
    assert "faster" in result.stdout
