import json
import hmac
import hashlib

os.environ["META_ACCESS_TOKEN"] = "test_access_token"
os.environ["META_ACCOUNT_ID"] = "test_account_id"
os.environ["META_WEBHOOK_VERIFY_TOKEN"] = "your_webhook_verify_token_here"
os.environ["META_APP_SECRET"] = "your_meta_app_secret_here"
os.environ["API_KEY"] = "test_api_key"

from unittest.mock import patch, AsyncMock, MagicMock
import pytest
import httpx
from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
settings.api_key = "test_api_key"

client = TestClient(app, raise_server_exceptions=False)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_webhook_get_success():
    response = client.get("/webhook?hub.mode=subscribe&hub.challenge=1158201444&hub.verify_token=your_webhook_verify_token_here")
    assert response.status_code == 200
    assert response.text == "1158201444"

def test_webhook_get_failure():
    response = client.get("/webhook?hub.mode=subscribe&hub.challenge=1158201444&hub.verify_token=wrong_token")
    assert response.status_code == 403


def test_webhook_post():
    payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "0",
                "time": 1520622968,
                "changes": [
                    {
                        "field": "comments",
                        "value": {
                            "id": "17881682464166275",
                            "text": "This is a comment"
                        }
                    }
                ]
            }
        ]
    }
    body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(
        settings.meta_app_secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "X-Hub-Signature-256": f"sha256={signature}",
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_webhook_post_missing_signature():
    payload = {"object": "instagram", "entry": []}
    response = client.post("/webhook", json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing signature"}

def test_webhook_post_invalid_signature():
    payload = {"object": "instagram", "entry": []}
    response = client.post(
        "/webhook",
        json=payload,
        headers={"X-Hub-Signature-256": "sha256=invalid"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid signature"}

@patch("app.main.social_media_service.get_posts", new_callable=AsyncMock)
def test_get_posts(mock_get_posts):
    """Test the get_posts endpoint."""
    mock_get_posts.return_value = {
        "data": [
            {
                "id": "123456789_987654321",
                "message": "This is a mock post message.",
                "created_time": "2024-03-03T10:00:00+0000"
            }
        ],
        "paging": {
            "cursors": {
                "before": "QVFIU...",
                "after": "QVFIU..."
            },
            "next": "https://graph.facebook.com/v19.0/123456789/posts?limit=2&after=QVFIU..."
        }
    }
    response = client.get("/posts")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "id": "123456789_987654321",
                "message": "This is a mock post message.",
                "created_time": "2024-03-03T10:00:00+0000"
            }
        ],
        "paging": {
            "cursors": {
                "before": "QVFIU...",
                "after": "QVFIU..."
            },
            "next": "https://graph.facebook.com/v19.0/123456789/posts?limit=2&after=QVFIU..."
        }
    }

@patch("app.main.social_media_service.get_posts", new_callable=AsyncMock)
def test_get_posts_internal_error(mock_get_posts):
    """Test the get_posts endpoint when an internal error occurs."""
    mock_get_posts.side_effect = Exception("Internal error")

    client_local = TestClient(app, raise_server_exceptions=False)
    response = client_local.get("/posts")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

@patch("app.adapters.meta_api.MetaGraphAPIClient.get_likes", new_callable=AsyncMock)
def test_get_likes(mock_get_likes):
    mock_get_likes.return_value = {"data": [{"id": "123", "name": "Test User"}]}
    response = client.get("/test_object_id/likes")
    assert response.status_code == 200
    assert response.json() == {"data": [{"id": "123", "name": "Test User"}], "paging": None}


@patch("app.adapters.meta_api.MetaGraphAPIClient.get_comments", new_callable=AsyncMock)
def test_get_comments(mock_get_comments):
    mock_get_comments.return_value = {
        "data": [{"id": "1", "message": "Test comment", "created_time": "2024-01-01T00:00:00+0000"}]
    }
    response = client.get("/posts/test_post_id/comments")
    assert response.status_code == 200
    assert response.json() == {
        "data": [{"id": "1", "message": "Test comment", "created_time": "2024-01-01T00:00:00+0000"}],
        "paging": None
    }

@patch("app.adapters.meta_api.MetaGraphAPIClient.get_comments", new_callable=AsyncMock)
def test_get_comments_http_error(mock_get_comments):
    mock_request = httpx.Request("GET", "https://graph.facebook.com/v18.0/test_post_id/comments")
    mock_response = httpx.Response(404, request=mock_request)
    mock_get_comments.side_effect = httpx.HTTPStatusError("Not Found", request=mock_request, response=mock_response)

    response = client.get("/posts/test_post_id/comments")
    assert response.status_code == 404
    assert response.json() == {"detail": "Meta API request failed"}

@patch("app.adapters.meta_api.MetaGraphAPIClient.get_comments", new_callable=AsyncMock)
def test_get_comments_http_error_with_json(mock_get_comments):
    mock_request = httpx.Request("GET", "https://graph.facebook.com/v18.0/test_post_id/comments")
    json_error_payload = {"error": {"message": "Invalid OAuth access token.", "type": "OAuthException", "code": 190, "fbtrace_id": "ABC"}}
    mock_response = httpx.Response(401, request=mock_request, json=json_error_payload)
    mock_get_comments.side_effect = httpx.HTTPStatusError("Unauthorized", request=mock_request, response=mock_response)

    response = client.get("/posts/test_post_id/comments")
    assert response.status_code == 401
    assert response.json() == {"detail": json_error_payload}

@patch("app.adapters.meta_api.MetaGraphAPIClient.get_comments", new_callable=AsyncMock)
def test_get_comments_internal_error(mock_get_comments):
    mock_get_comments.side_effect = Exception("Internal error")

    response = client.get("/posts/test_post_id/comments")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


@pytest.mark.asyncio
@patch("app.main.api_logger.log_call")
async def test_log_requests_middleware_exception(mock_log_call):
    from app.main import log_requests
    mock_request = MagicMock(spec=Request)
    mock_request.method = "GET"
    mock_request.url.path = "/test-middleware-error"

    async def mock_call_next(request):
        raise RuntimeError("Simulated middleware error")

    with pytest.raises(RuntimeError, match="Simulated middleware error"):
        await log_requests(mock_request, mock_call_next)

    mock_log_call.assert_called_once()
    _, kwargs = mock_log_call.call_args
    assert kwargs.get("call_type") == "incoming"
    assert kwargs.get("method") == "GET"
    assert kwargs.get("url") == "/test-middleware-error"
    assert kwargs.get("status_code") == 500
    assert kwargs.get("error") == "Simulated middleware error"

@pytest.mark.asyncio
async def test_http_status_error_handler_with_json():
    from app.main import http_status_error_handler
    from fastapi import Request
    from unittest.mock import MagicMock
    import json

    mock_request = MagicMock(spec=Request)
    mock_request_httpx = httpx.Request("GET", "https://graph.facebook.com/v18.0/test")
    mock_response = httpx.Response(400, request=mock_request_httpx, json={"error": {"message": "Invalid parameter"}})
    exc = httpx.HTTPStatusError("Bad Request", request=mock_request_httpx, response=mock_response)

    response = await http_status_error_handler(mock_request, exc)

    assert response.status_code == 400
    assert json.loads(response.body) == {"detail": {"error": {"message": "Invalid parameter"}}}

@pytest.mark.asyncio
async def test_http_status_error_handler_without_json():
    from app.main import http_status_error_handler
    from fastapi import Request
    from unittest.mock import MagicMock
    import json

    mock_request = MagicMock(spec=Request)
    mock_request_httpx = httpx.Request("GET", "https://graph.facebook.com/v18.0/test")
    mock_response = httpx.Response(500, request=mock_request_httpx, content=b"Internal Server Error Text")
    exc = httpx.HTTPStatusError("Internal Server Error", request=mock_request_httpx, response=mock_response)

    response = await http_status_error_handler(mock_request, exc)

    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "Meta API request failed"}

@pytest.mark.asyncio
async def test_http_status_error_handler_missing_response():
    from app.main import http_status_error_handler
    from fastapi import Request
    from unittest.mock import MagicMock
    import json

    mock_request = MagicMock(spec=Request)
    mock_request_httpx = httpx.Request("GET", "https://graph.facebook.com/v18.0/test")
    exc = httpx.HTTPStatusError("Error", request=mock_request_httpx, response=None) # type: ignore

    response = await http_status_error_handler(mock_request, exc)

    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "Meta API request failed"}


@pytest.mark.asyncio
async def test_generic_exception_handler_standard_exception():
    from app.main import generic_exception_handler
    from fastapi import Request
    from unittest.mock import MagicMock
    import json

    mock_request = MagicMock(spec=Request)
    exc = Exception("A standard exception occurred")

    response = await generic_exception_handler(mock_request, exc)

    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "Internal server error"}

@pytest.mark.asyncio
async def test_generic_exception_handler_starlette_http_exception():
    from app.main import generic_exception_handler
    from fastapi import Request
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from unittest.mock import MagicMock
    import json

    mock_request = MagicMock(spec=Request)
    exc = StarletteHTTPException(status_code=403, detail="Forbidden access")

    response = await generic_exception_handler(mock_request, exc)

    assert response.status_code == 403
    assert json.loads(response.body) == {"detail": "Forbidden access"}


def test_generic_exception_handler_integration_standard():
    client_local = TestClient(app, raise_server_exceptions=False)
    with patch("app.main.api_logger.get_logs", side_effect=Exception("Integration error")):
        response = client_local.get("/logs", headers={"X-API-Key": "test_api_key"})
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}

def test_generic_exception_handler_integration_starlette():
    client_local = TestClient(app, raise_server_exceptions=False)
    from starlette.exceptions import HTTPException as StarletteHTTPException
    with patch("app.main.api_logger.get_logs", side_effect=StarletteHTTPException(status_code=401, detail="Unauthorized integration")):
        response = client_local.get("/logs", headers={"X-API-Key": "test_api_key"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized integration"}

@patch("app.main.social_media_service.like_object", new_callable=AsyncMock)
def test_like_comment_success(mock_like_object):
    mock_like_object.return_value = {"success": True}
    response = client.post("/comments/test_comment_id/like")
    assert response.status_code == 200
    assert response.json() == {"success": True}

@patch("app.main.social_media_service.like_object", new_callable=AsyncMock)
def test_like_comment_internal_error(mock_like_object):
    mock_like_object.side_effect = Exception("Internal error")

    response = client.post("/comments/test_comment_id/like")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
