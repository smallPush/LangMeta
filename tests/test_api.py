import os
import json
import hmac
import hashlib

os.environ["META_ACCESS_TOKEN"] = "test_access_token"
os.environ["META_ACCOUNT_ID"] = "test_account_id"
os.environ["META_WEBHOOK_VERIFY_TOKEN"] = "your_webhook_verify_token_here"

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
import httpx
from unittest.mock import patch, AsyncMock, MagicMock

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

import hmac
import hashlib
import json

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

@patch("app.adapters.meta_api.MetaGraphAPIClient.get_likes", new_callable=AsyncMock)
def test_get_likes(mock_get_likes):
    mock_get_likes.return_value = {"data": [{"id": "123", "name": "Test User"}]}
    response = client.get("/test_object_id/likes")
    assert response.status_code == 200
    assert response.json() == {"data": [{"id": "123", "name": "Test User"}], "paging": None}


import httpx

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
    assert response.json() == {"detail": "Not Found"}

@patch("app.adapters.meta_api.MetaGraphAPIClient.get_comments", new_callable=AsyncMock)
def test_get_comments_internal_error(mock_get_comments):
    mock_get_comments.side_effect = Exception("Internal error")

    response = client.get("/posts/test_post_id/comments")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal error"}
