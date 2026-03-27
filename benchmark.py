import asyncio
import time
from app.adapters.meta_api import MetaGraphAPIClient
from unittest.mock import patch

# Mock data
posts_data = {
    "data": [
        {
            "id": f"post_{i}",
            "likes": {"data": [{"id": f"like_{j}"} for j in range(2)]},
            "comments": {"data": [{"id": f"comment_{j}", "likes": {"data": [{"id": f"like_{k}"} for k in range(2)]}} for j in range(5)]}
        } for i in range(5)
    ]
}

async def mock_get_posts(*args, **kwargs):
    await asyncio.sleep(0.1)
    return posts_data

async def run_benchmark():
    # Patch the methods on the instance or class
    with patch.object(MetaGraphAPIClient, 'get_posts', side_effect=mock_get_posts):

        # Import inside to make sure it uses the patched client if it imports it directly,
        # but cron imports meta_client from app.adapters.meta_api
        import cron

        start_time = time.time()
        await cron.fetch_and_process()
        end_time = time.time()

        print(f"\nExecution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
