import time
import urllib.parse

class OriginalSanitizer:
    def __init__(self, access_token):
        self.access_token = access_token

    def _sanitize_string(self, text: str) -> str:
        if not text:
            return text
        encoded_token = urllib.parse.quote(self.access_token)
        encoded_token_plus = urllib.parse.quote_plus(self.access_token)
        return text.replace(self.access_token, "***").replace(encoded_token, "***").replace(encoded_token_plus, "***")


class OptimizedSanitizer:
    def __init__(self, access_token):
        self.access_token = access_token
        self._encoded_token = urllib.parse.quote(self.access_token)
        self._encoded_token_plus = urllib.parse.quote_plus(self.access_token)

    def _sanitize_string(self, text: str) -> str:
        if not text:
            return text
        return text.replace(self.access_token, "***").replace(self._encoded_token, "***").replace(self._encoded_token_plus, "***")

def run_benchmark():
    access_token = "my_super_secret_access_token_which_is_long_and_needs_encoding!"
    test_string = f"An error occurred while fetching data using the access token: {access_token}. The encoded version is {urllib.parse.quote(access_token)} and {urllib.parse.quote_plus(access_token)}."

    orig = OriginalSanitizer(access_token)
    opt = OptimizedSanitizer(access_token)

    iterations = 100000

    # Original
    start = time.perf_counter()
    for _ in range(iterations):
        orig._sanitize_string(test_string)
    orig_time = time.perf_counter() - start

    # Optimized
    start = time.perf_counter()
    for _ in range(iterations):
        opt._sanitize_string(test_string)
    opt_time = time.perf_counter() - start

    print(f"Original: {orig_time:.4f}s")
    print(f"Optimized: {opt_time:.4f}s")
    print(f"Improvement: {orig_time / opt_time:.2f}x faster ({(orig_time - opt_time) / orig_time * 100:.2f}%)")

if __name__ == '__main__':
    run_benchmark()
