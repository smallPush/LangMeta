from typing import Dict, Any
from app.application.ports.meta_port import MetaPort

class MetaService:
    def __init__(self, meta_port: MetaPort):
        self.meta_port = meta_port

    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        return await self.meta_port.get_posts(limit=limit)

    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        return await self.meta_port.get_comments(post_id, limit=limit)

    async def post_comment(self, object_id: str, message: str) -> Dict[str, Any]:
        return await self.meta_port.post_comment(object_id, message)

    async def like_object(self, object_id: str) -> Dict[str, Any]:
        return await self.meta_port.like_object(object_id)

    async def get_likes(self, object_id: str, limit: int = 10) -> Dict[str, Any]:
        return await self.meta_port.get_likes(object_id, limit=limit)
