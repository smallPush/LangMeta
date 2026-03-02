import asyncio
import time
from app.meta_api import MetaGraphAPIClient
import httpx
from unittest.mock import patch, MagicMock

# Mock data
posts_data = {
    "data": [{"id": f"post_{i}"} for i in range(5)]
}
comments_data = {
    "data": [{"id": f"comment_{i}"} for i in range(5)]
}
likes_data = {
    "data": [{"id": f"like_{i}"} for i in range(2)]
}

async def mock_get_posts(*args, **kwargs):
    await asyncio.sleep(0.1)
    return posts_data

async def mock_get_comments(*args, **kwargs):
    await asyncio.sleep(0.1)
    return comments_data

async def mock_get_likes(*args, **kwargs):
    await asyncio.sleep(0.1)
    return likes_data

async def run_benchmark():
    # Patch the methods on the instance or class
    with patch.object(MetaGraphAPIClient, 'get_posts', side_effect=mock_get_posts), \
         patch.object(MetaGraphAPIClient, 'get_comments', side_effect=mock_get_comments), \
         patch.object(MetaGraphAPIClient, 'get_likes', side_effect=mock_get_likes):

        # Import inside to make sure it uses the patched client if it imports it directly,
        # but cron imports meta_client from app.meta_api
        import cron

        start_time = time.time()
        await cron.fetch_and_process()
        end_time = time.time()

        print(f"\nExecution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
