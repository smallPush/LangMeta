from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest

from app.ports.social_media import SocialMediaPort
from app.services.social_media_service import SocialMediaService


class MockSocialMediaClient(SocialMediaPort):
    def __init__(self):
        self.aclose_mock = AsyncMock()
        self.get_posts_mock = AsyncMock()
        self.get_comments_mock = AsyncMock()
        self.post_comment_mock = AsyncMock()
        self.like_object_mock = AsyncMock()
        self.get_likes_mock = AsyncMock()

    async def aclose(self):
        return await self.aclose_mock()

    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        return await self.get_posts_mock(limit=limit)

    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        return await self.get_comments_mock(post_id=post_id, limit=limit)

    async def post_comment(self, object_id: str, message: str) -> Dict[str, Any]:
        return await self.post_comment_mock(object_id=object_id, message=message)

    async def like_object(self, object_id: str) -> Dict[str, Any]:
        return await self.like_object_mock(object_id=object_id)

    async def get_likes(self, object_id: str, limit: int = 10) -> Dict[str, Any]:
        return await self.get_likes_mock(object_id=object_id, limit=limit)

@pytest.fixture
def mock_client():
    return MockSocialMediaClient()

@pytest.fixture
def service(mock_client):
    return SocialMediaService(client=mock_client)

@pytest.mark.asyncio
async def test_aclose(service, mock_client):
    await service.aclose()
    mock_client.aclose_mock.assert_called_once()

@pytest.mark.asyncio
async def test_get_posts(service, mock_client):
    expected_response = {"data": [{"id": "1", "message": "Test Post"}]}
    mock_client.get_posts_mock.return_value = expected_response

    result = await service.get_posts(limit=5)

    mock_client.get_posts_mock.assert_called_once_with(limit=5)
    assert result == expected_response

@pytest.mark.asyncio
async def test_get_comments(service, mock_client):
    expected_response = {"data": [{"id": "2", "message": "Test Comment"}]}
    mock_client.get_comments_mock.return_value = expected_response

    result = await service.get_comments(post_id="post123", limit=10)

    mock_client.get_comments_mock.assert_called_once_with(post_id="post123", limit=10)
    assert result == expected_response

@pytest.mark.asyncio
async def test_post_comment(service, mock_client):
    expected_response = {"id": "new_comment_id"}
    mock_client.post_comment_mock.return_value = expected_response

    result = await service.post_comment(object_id="obj123", message="Hello!")

    mock_client.post_comment_mock.assert_called_once_with(object_id="obj123", message="Hello!")
    assert result == expected_response

@pytest.mark.asyncio
async def test_like_object(service, mock_client):
    expected_response = {"success": True}
    mock_client.like_object_mock.return_value = expected_response

    result = await service.like_object(object_id="obj123")

    mock_client.like_object_mock.assert_called_once_with(object_id="obj123")
    assert result == expected_response

@pytest.mark.asyncio
async def test_get_likes(service, mock_client):
    expected_response = {"data": [{"id": "user123", "name": "John Doe"}]}
    mock_client.get_likes_mock.return_value = expected_response

    result = await service.get_likes(object_id="obj123", limit=20)

    mock_client.get_likes_mock.assert_called_once_with(object_id="obj123", limit=20)
    assert result == expected_response
