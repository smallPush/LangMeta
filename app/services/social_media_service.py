from typing import Dict, Any
from app.ports.social_media import SocialMediaPort

class SocialMediaService:
    def __init__(self, client: SocialMediaPort):
        self.client = client

    async def aclose(self):
        await self.client.aclose()

    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        return await self.client.get_posts(limit=limit)

    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        return await self.client.get_comments(post_id=post_id, limit=limit)

    async def post_comment(self, object_id: str, message: str) -> Dict[str, Any]:
        return await self.client.post_comment(object_id=object_id, message=message)

    async def like_object(self, object_id: str) -> Dict[str, Any]:
        return await self.client.like_object(object_id=object_id)

    async def get_likes(self, object_id: str, limit: int = 10) -> Dict[str, Any]:
        return await self.client.get_likes(object_id=object_id, limit=limit)
