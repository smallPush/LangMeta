import httpx
from typing import Dict, Any, Optional
from app.config import settings

class MetaGraphAPIClient:
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.meta_api_version}"
        self.access_token = settings.meta_access_token
        self.account_id = settings.meta_account_id

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        if not params:
            params = {}
        params["access_token"] = self.access_token

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        params = {"access_token": self.access_token}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, json=data)
            response.raise_for_status()
            return response.json()

    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        """Fetch posts from the configured account."""
        endpoint = f"{self.account_id}/posts"
        params = {"limit": limit, "fields": "id,message,created_time"}
        return await self._get(endpoint, params)

    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        """Fetch comments for a specific post."""
        endpoint = f"{post_id}/comments"
        params = {"limit": limit, "fields": "id,message,created_time"}
        return await self._get(endpoint, params)

    async def post_comment(self, object_id: str, message: str) -> Dict[str, Any]:
        """Post a comment on a specific object (post or comment)."""
        endpoint = f"{object_id}/comments"
        data = {"message": message}
        return await self._post(endpoint, data=data)

    async def like_object(self, object_id: str) -> Dict[str, Any]:
        """Like a specific object (post or comment)."""
        endpoint = f"{object_id}/likes"
        return await self._post(endpoint)

meta_client = MetaGraphAPIClient()
