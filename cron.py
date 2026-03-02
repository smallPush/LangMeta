import asyncio
from app.infrastructure.adapters.meta_api_adapter import MetaAPIAdapter
from app.application.services.meta_service import MetaService

async def fetch_and_process():
    print("Running cron job to fetch posts, comments, and likes...")
    try:
        adapter = MetaAPIAdapter()
        service = MetaService(adapter)

        # Fetch posts
        posts_response = await service.get_posts(limit=5)
        posts = posts_response.get("data", [])

        for post in posts:
            post_id = post.get("id")
            print(f"Processing post: {post_id}")

            # Fetch likes for the post
            post_likes_response = await service.get_likes(post_id, limit=5)
            post_likes = post_likes_response.get("data", [])
            print(f"  Post {post_id} has {len(post_likes)} likes.")

            # Fetch comments for the post
            comments_response = await service.get_comments(post_id, limit=5)
            comments = comments_response.get("data", [])

            for comment in comments:
                comment_id = comment.get("id")
                print(f"  Processing comment: {comment_id}")

                # Fetch likes for the comment
                comment_likes_response = await service.get_likes(comment_id, limit=5)
                comment_likes = comment_likes_response.get("data", [])
                print(f"    Comment {comment_id} has {len(comment_likes)} likes.")

    except Exception as e:
        print(f"An error occurred during cron execution: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_process())
