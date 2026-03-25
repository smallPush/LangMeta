import httpx
from typing import Dict, Any, Optional
import time
import urllib.parse
from app.config import settings
from app.ports.social_media import SocialMediaPort
from app.services.logger_service import api_logger

class MetaGraphAPIClient(SocialMediaPort):
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.base_url = f"https://graph.facebook.com/{settings.meta_api_version}"
        self.access_token = settings.meta_access_token
        self.account_id = settings.meta_account_id
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient()

    def _sanitize_string(self, text: str) -> str:
        if not text:
            return text
        encoded_token = urllib.parse.quote(self.access_token)
        encoded_token_plus = urllib.parse.quote_plus(self.access_token)
        return text.replace(self.access_token, "***").replace(encoded_token, "***").replace(encoded_token_plus, "***")

    async def aclose(self):
        """Close the underlying HTTP client."""
        if self._owns_client:
            await self.client.aclose()

    async def _request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        if not params:
            params = {}
        params["access_token"] = self.access_token

        start_time = time.time()
        try:
            request = self.client.build_request(method, url, params=params, json=data)
            response = await self.client.send(request)
            process_time_ms = (time.time() - start_time) * 1000
            api_logger.log_call(
                call_type="outgoing",
                method=method,
                url=url,
                status_code=response.status_code,
                response_time_ms=process_time_ms
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            process_time_ms = (time.time() - start_time) * 1000
            status_code = getattr(exc, "response", None).status_code if getattr(exc, "response", None) else 500
            api_logger.log_call(
                call_type="outgoing",
                method=method,
                url=url,
                status_code=status_code,
                response_time_ms=process_time_ms,
                error=self._sanitize_string(str(exc))
            )
            raise

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request("GET", endpoint, params=params)

    async def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request("POST", endpoint, data=data)

    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        """Fetch posts from the configured account."""
        endpoint = f"{self.account_id}/posts"
        params = {"limit": limit, "fields": "id,message,created_time"}
        return await self._get(endpoint, params)

    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        """Fetch comments for a specific post."""
        endpoint = f"{post_id}/comments"
        params = {"limit": limit, "fields": "id,message,created_time,likes.limit(5)"}
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

    async def get_likes(self, object_id: str, limit: int = 10) -> Dict[str, Any]:
        """Fetch likes for a specific object (post or comment)."""
        endpoint = f"{object_id}/likes"
        params = {"limit": limit}
        return await self._get(endpoint, params)
