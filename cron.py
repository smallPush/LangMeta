import asyncio

import httpx

from app.adapters.meta_api import MetaGraphAPIClient
from app.services.social_media_service import SocialMediaService


async def process_comment(service, comment):
    comment_id = comment.get("id")
    print(f"  Processing comment: {comment_id}")
    comment_likes_response = comment.get("likes", {})
    comment_likes = comment_likes_response.get("data", [])
    print(f"    Comment {comment_id} has {len(comment_likes)} likes.")

async def fetch_and_process():
    print("Running cron job to fetch posts, comments, and likes...")
    try:
        http_client = httpx.AsyncClient()
        client = MetaGraphAPIClient(client=http_client)
        service = SocialMediaService(client)
        
        # Fetch posts
        posts_response = await service.get_posts(limit=5)
        posts = posts_response.get("data", [])

        # Fetch likes and comments for all posts concurrently
        async def process_post(post):
            post_id = post.get("id")
            print(f"Processing post: {post_id}")

            # Fetch likes and comments for the post concurrently
            post_likes_response, comments_response = await asyncio.gather(
                service.get_likes(post_id, limit=5),
                service.get_comments(post_id, limit=5)
            )

            post_likes = post_likes_response.get("data", [])
            print(f"  Post {post_id} has {len(post_likes)} likes.")

            comments = comments_response.get("data", [])

            # Fetch likes for all comments concurrently
            await asyncio.gather(*(process_comment(service, comment) for comment in comments))

        await asyncio.gather(*(process_post(post) for post in posts))

        await client.aclose()
        await http_client.aclose()
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"An error occurred during cron execution: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_process())
