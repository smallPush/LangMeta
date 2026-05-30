import asyncio
import httpx
from app.adapters.meta_api import MetaGraphAPIClient
from app.services.social_media_service import SocialMediaService

async def process_comment(comment):
    comment_id = comment.get("id")
    print(f"  Processing comment: {comment_id}")
    comment_likes_response = comment.get("likes", {})
    comment_likes = comment_likes_response.get("data", [])
    print(f"    Comment {comment_id} has {len(comment_likes)} likes.")

async def bounded_process_comment(comment, semaphore):
    async with semaphore:
        await process_comment(comment)

async def process_post(post, semaphore):
    async with semaphore:
        post_id = post.get("id")
        print(f"Processing post: {post_id}")

        post_likes = post.get("likes", {}).get("data", [])
        print(f"  Post {post_id} has {len(post_likes)} likes.")

        comments = post.get("comments", {}).get("data", [])

    # Fetch likes for all comments concurrently
    await asyncio.gather(*(bounded_process_comment(comment, semaphore) for comment in comments))

async def fetch_and_process():
    print("Running cron job to fetch posts, comments, and likes...")
    try:
        async with httpx.AsyncClient() as http_client:
            client = MetaGraphAPIClient(client=http_client)
            service = SocialMediaService(client)

            # Fetch posts
            posts_response = await service.get_posts(limit=5)
            posts = posts_response.get("data", [])

            semaphore = asyncio.Semaphore(10)

            await asyncio.gather(*(process_post(post, semaphore) for post in posts))

            await client.aclose()
    except Exception as e:
        print(f"An error occurred during cron execution: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_process())
