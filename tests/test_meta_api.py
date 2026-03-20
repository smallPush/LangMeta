import os
os.environ["META_ACCESS_TOKEN"] = "test_access_token"
os.environ["META_ACCOUNT_ID"] = "test_account_id"
os.environ["META_WEBHOOK_VERIFY_TOKEN"] = "your_webhook_verify_token_here"
os.environ["META_APP_SECRET"] = "your_meta_app_secret_here"
os.environ["API_KEY"] = "test_api_key"

import pytest
import httpx
from unittest.mock import patch, AsyncMock
from app.adapters.meta_api import MetaGraphAPIClient

@pytest.fixture
def meta_client():
    return MetaGraphAPIClient()

@pytest.mark.asyncio
async def test_get_success(meta_client):
    endpoint = "test_endpoint"
    params = {"test_param": "test_value"}
    expected_url = f"{meta_client.base_url}/{endpoint}"
    expected_params = {"test_param": "test_value", "access_token": meta_client.access_token}
    mock_response = AsyncMock()
    mock_response.json = lambda: {"data": "test_data"}
    mock_response.raise_for_status = lambda: None

    with patch.object(meta_client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await meta_client._get(endpoint, params)

        mock_get.assert_called_once_with(expected_url, params=expected_params)
        assert result == {"data": "test_data"}

@pytest.mark.asyncio
async def test_get_failure(meta_client):
    endpoint = "test_endpoint"
    mock_response = AsyncMock()

    def raise_error():
        raise httpx.HTTPStatusError("Error", request=AsyncMock(), response=AsyncMock())

    mock_response.raise_for_status = raise_error

    with patch.object(meta_client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await meta_client._get(endpoint)

@pytest.mark.asyncio
async def test_post_success(meta_client):
    endpoint = "test_endpoint"
    data = {"test_data": "test_value"}
    expected_url = f"{meta_client.base_url}/{endpoint}"
    expected_params = {"access_token": meta_client.access_token}
    mock_response = AsyncMock()
    mock_response.json = lambda: {"id": "test_id"}
    mock_response.raise_for_status = lambda: None

    with patch.object(meta_client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await meta_client._post(endpoint, data)

        mock_post.assert_called_once_with(expected_url, params=expected_params, json=data)
        assert result == {"id": "test_id"}

@pytest.mark.asyncio
async def test_post_failure(meta_client):
    endpoint = "test_endpoint"
    mock_response = AsyncMock()

    def raise_error():
        raise httpx.HTTPStatusError("Error", request=AsyncMock(), response=AsyncMock())

    mock_response.raise_for_status = raise_error

    with patch.object(meta_client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await meta_client._post(endpoint)

@pytest.mark.asyncio
async def test_get_posts(meta_client):
    limit = 5
    expected_endpoint = f"{meta_client.account_id}/posts"
    expected_params = {"limit": limit, "fields": "id,message,created_time"}

    with patch.object(meta_client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"data": []}
        result = await meta_client.get_posts(limit=limit)

        mock_get.assert_called_once_with(expected_endpoint, expected_params)
        assert result == {"data": []}

@pytest.mark.asyncio
async def test_get_comments(meta_client):
    post_id = "test_post_id"
    limit = 5
    expected_endpoint = f"{post_id}/comments"
    expected_params = {"limit": limit, "fields": "id,message,created_time"}

    with patch.object(meta_client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"data": []}
        result = await meta_client.get_comments(post_id, limit=limit)

        mock_get.assert_called_once_with(expected_endpoint, expected_params)
        assert result == {"data": []}

@pytest.mark.asyncio
async def test_post_comment(meta_client):
    object_id = "test_object_id"
    message = "test message"
    expected_endpoint = f"{object_id}/comments"
    expected_data = {"message": message}

    with patch.object(meta_client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"id": "new_comment_id"}
        result = await meta_client.post_comment(object_id, message)

        mock_post.assert_called_once_with(expected_endpoint, data=expected_data)
        assert result == {"id": "new_comment_id"}

@pytest.mark.asyncio
async def test_like_object(meta_client):
    object_id = "test_object_id"
    expected_endpoint = f"{object_id}/likes"

    with patch.object(meta_client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"success": True}
        result = await meta_client.like_object(object_id)

        mock_post.assert_called_once_with(expected_endpoint)
        assert result == {"success": True}

@pytest.mark.asyncio
async def test_get_likes(meta_client):
    object_id = "test_object_id"
    limit = 20
    expected_endpoint = f"{object_id}/likes"
    expected_params = {"limit": limit}

    with patch.object(meta_client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"data": []}
        result = await meta_client.get_likes(object_id, limit=limit)

        mock_get.assert_called_once_with(expected_endpoint, expected_params)
        assert result == {"data": []}
