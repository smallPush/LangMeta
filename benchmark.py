import asyncio
import time
from app.meta_api import MetaGraphAPIClient
import httpx
from unittest.mock import patch, MagicMock

class MockResponse:
    def __init__(self):
        self.status_code = 200
    def raise_for_status(self):
        pass
    def json(self):
        return {"id": "123", "message": "hello"}

async def mock_get(*args, **kwargs):
    return MockResponse()

async def mock_post(*args, **kwargs):
    return MockResponse()

async def run_benchmark():
    client = MetaGraphAPIClient()

    # We patch httpx.AsyncClient.get and post to just return a mock response,
    # so we're only measuring the overhead of client creation and python execution.
    with patch('httpx.AsyncClient.get', side_effect=mock_get), \
         patch('httpx.AsyncClient.post', side_effect=mock_post):

        # Warmup
        for _ in range(10):
            await client.get_posts()

        start = time.perf_counter()
        for _ in range(1000):
            await client.get_posts()
        get_time = time.perf_counter() - start

        start = time.perf_counter()
        for _ in range(1000):
            await client.post_comment("123", "msg")
        post_time = time.perf_counter() - start

        print(f"Baseline - 1000 GET requests: {get_time:.4f}s")
        print(f"Baseline - 1000 POST requests: {post_time:.4f}s")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
