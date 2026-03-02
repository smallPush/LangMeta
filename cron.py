import asyncio
from app.meta_api import meta_client

async def fetch_and_process():
    print("Running cron job to fetch posts, comments, and likes...")
    try:
        # Fetch posts
        posts_response = await meta_client.get_posts(limit=5)
        posts = posts_response.get("data", [])

        for post in posts:
            post_id = post.get("id")
            print(f"Processing post: {post_id}")

            # Fetch likes and comments for the post concurrently
            post_likes_response, comments_response = await asyncio.gather(
                meta_client.get_likes(post_id, limit=5),
                meta_client.get_comments(post_id, limit=5)
            )

            post_likes = post_likes_response.get("data", [])
            print(f"  Post {post_id} has {len(post_likes)} likes.")

            comments = comments_response.get("data", [])

            # Fetch likes for all comments concurrently
            async def process_comment(comment):
                comment_id = comment.get("id")
                print(f"  Processing comment: {comment_id}")
                comment_likes_response = await meta_client.get_likes(comment_id, limit=5)
                comment_likes = comment_likes_response.get("data", [])
                print(f"    Comment {comment_id} has {len(comment_likes)} likes.")

            await asyncio.gather(*(process_comment(comment) for comment in comments))

    except Exception as e:
        print(f"An error occurred during cron execution: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_process())
