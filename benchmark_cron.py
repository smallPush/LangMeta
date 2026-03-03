import asyncio
import time
from unittest.mock import AsyncMock, patch
import cron

async def mock_get_posts(limit=10):
    await asyncio.sleep(0.1)
    return {"data": [{"id": f"post_{i}"} for i in range(limit)]}

async def mock_get_comments(post_id, limit=10):
    await asyncio.sleep(0.1)
    return {"data": [{"id": f"comment_{post_id}_{i}"} for i in range(limit)]}

async def mock_get_likes(object_id, limit=10):
    await asyncio.sleep(0.1)
    return {"data": [{"id": f"like_{object_id}_{i}"} for i in range(limit)]}

async def run_benchmark():
    with patch("app.services.social_media_service.SocialMediaService.get_posts", new_callable=AsyncMock, side_effect=mock_get_posts), \
         patch("app.services.social_media_service.SocialMediaService.get_comments", new_callable=AsyncMock, side_effect=mock_get_comments), \
         patch("app.services.social_media_service.SocialMediaService.get_likes", new_callable=AsyncMock, side_effect=mock_get_likes):

        start_time = time.perf_counter()
        await cron.fetch_and_process()
        end_time = time.perf_counter()

        print(f"\nExecution Time: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
