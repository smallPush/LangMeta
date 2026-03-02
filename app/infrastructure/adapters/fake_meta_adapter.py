from typing import Dict, Any
from app.application.ports.meta_port import MetaPort

class FakeMetaAdapter(MetaPort):
    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        return {
            "data": [
                {"id": "post1", "message": "Fake post 1", "created_time": "2023-01-01T00:00:00+0000"},
                {"id": "post2", "message": "Fake post 2", "created_time": "2023-01-02T00:00:00+0000"}
            ][:limit]
        }

    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        return {
            "data": [
                {"id": "comment1", "message": f"Fake comment on {post_id}", "created_time": "2023-01-01T01:00:00+0000"}
            ][:limit]
        }

    async def post_comment(self, object_id: str, message: str) -> Dict[str, Any]:
        return {"id": "new_comment_id"}

    async def like_object(self, object_id: str) -> Dict[str, Any]:
        return {"success": True}

    async def get_likes(self, object_id: str, limit: int = 10) -> Dict[str, Any]:
        return {
            "data": [
                {"id": "user1", "name": "Fake User 1"},
                {"id": "user2", "name": "Fake User 2"}
            ][:limit]
        }
