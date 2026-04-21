import pytest
import httpx
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_get_success(meta_client):
    endpoint = "test_endpoint"
    params = {"test_param": "test_value"}
    mock_response = AsyncMock()
    mock_response.json = lambda: {"data": "test_data"}
    mock_response.raise_for_status = lambda: None

    with patch.object(meta_client.client, "send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = mock_response
        result = await meta_client._get(endpoint, params)

        assert mock_send.call_count == 1
        assert result == {"data": "test_data"}

@pytest.mark.asyncio
async def test_get_failure(meta_client):
    endpoint = "test_endpoint"
    mock_response = AsyncMock()

    def raise_error():
        raise httpx.HTTPStatusError("Error", request=AsyncMock(), response=AsyncMock())

    mock_response.raise_for_status = raise_error

    with patch.object(meta_client.client, "send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await meta_client._get(endpoint)

@pytest.mark.asyncio
async def test_post_success(meta_client):
    endpoint = "test_endpoint"
    data = {"test_data": "test_value"}
    mock_response = AsyncMock()
    mock_response.json = lambda: {"id": "test_id"}
    mock_response.raise_for_status = lambda: None

    with patch.object(meta_client.client, "send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = mock_response

        result = await meta_client._post(endpoint, data)

        assert mock_send.call_count == 1
        assert result == {"id": "test_id"}

@pytest.mark.asyncio
async def test_post_failure(meta_client):
    endpoint = "test_endpoint"
    mock_response = AsyncMock()

    def raise_error():
        raise httpx.HTTPStatusError("Error", request=AsyncMock(), response=AsyncMock())

    mock_response.raise_for_status = raise_error

    with patch.object(meta_client.client, "send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await meta_client._post(endpoint)

@pytest.mark.asyncio
async def test_get_posts(meta_client):
    limit = 5
    expected_endpoint = f"{meta_client.account_id}/posts"
    expected_params = {"limit": limit, "fields": "id,message,created_time,comments.limit(5){id,message,created_time,likes.limit(5)},likes.limit(5)"}

    with patch.object(meta_client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"data": []}
        result = await meta_client.get_posts(limit=limit)

        mock_get.assert_called_once_with(expected_endpoint, expected_params)
        assert result == {"data": []}


@pytest.mark.asyncio
async def test_aclose_owns_client():
    from app.adapters.meta_api import MetaGraphAPIClient
    client = MetaGraphAPIClient()
    with patch.object(client.client, "aclose", new_callable=AsyncMock) as mock_aclose:
        await client.aclose()
        mock_aclose.assert_called_once()

@pytest.mark.asyncio
async def test_aclose_does_not_own_client():
    from app.adapters.meta_api import MetaGraphAPIClient
    mock_httpx_client = AsyncMock()
    client = MetaGraphAPIClient(client=mock_httpx_client)
    await client.aclose()
    mock_httpx_client.aclose.assert_not_called()

@pytest.mark.asyncio
async def test_api_logger_sanitization_on_error(meta_client):
    from app.services.logger_service import api_logger
    import urllib.parse
    api_logger.clear_logs()

    endpoint = "test_error_sanitization"
    expected_url = f"{meta_client.base_url}/{endpoint}"
    mock_request = httpx.Request("GET", expected_url)

    # Simulate an error response with the token in the error message
    error_msg = f"Error with token {meta_client.access_token} and encoded {urllib.parse.quote(meta_client.access_token)}"
    mock_response = httpx.Response(500, request=mock_request)
    http_error = httpx.HTTPStatusError(error_msg, request=mock_request, response=mock_response)

    with patch.object(meta_client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = http_error

        with pytest.raises(httpx.HTTPStatusError):
            await meta_client._get(endpoint)

    logs = api_logger.get_logs()
    assert len(logs) == 1
    log = logs[0]

    assert log["error"] is not None
    assert meta_client.access_token not in log["error"]
    assert "***" in log["error"]

    assert meta_client.access_token not in log["url"]

@pytest.mark.asyncio
async def test_api_logger_sanitization_on_success(meta_client):
    from app.services.logger_service import api_logger
    api_logger.clear_logs()

    endpoint = "test_success_sanitization"
    mock_response = AsyncMock()
    mock_response.json = lambda: {"data": "test"}
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None

    with patch.object(meta_client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        await meta_client._post(endpoint, data={})

    logs = api_logger.get_logs()
    assert len(logs) == 1
    log = logs[0]

    assert meta_client.access_token not in log["url"]

@pytest.mark.asyncio
async def test_get_comments(meta_client):
    post_id = "test_post_id"
    limit = 5
    expected_endpoint = f"{post_id}/comments"
    expected_params = {"limit": limit, "fields": "id,message,created_time,likes.limit(5)"}

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
