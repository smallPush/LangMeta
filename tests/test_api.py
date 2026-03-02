from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

from unittest.mock import patch, AsyncMock
from app.config import settings

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
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

@patch("app.meta_api.MetaGraphAPIClient.get_likes", new_callable=AsyncMock)
def test_get_likes(mock_get_likes):
    mock_get_likes.return_value = {"data": [{"id": "123", "name": "Test User"}]}
    response = client.get("/test_object_id/likes")
    assert response.status_code == 200
    assert response.json() == {"data": [{"id": "123", "name": "Test User"}], "paging": None}

import httpx

@patch("app.meta_api.MetaGraphAPIClient.like_object", new_callable=AsyncMock)
def test_like_comment_success(mock_like_object):
    mock_like_object.return_value = {"success": True}
    response = client.post("/comments/12345/like")
    assert response.status_code == 200
    assert response.json() == {"success": True}
    mock_like_object.assert_called_once_with("12345")

@patch("app.meta_api.MetaGraphAPIClient.like_object", new_callable=AsyncMock)
def test_like_comment_http_error(mock_like_object):
    mock_response = httpx.Response(status_code=400, request=httpx.Request("POST", "https://example.com"), json={"error": "Bad Request"})
    mock_like_object.side_effect = httpx.HTTPStatusError("Bad Request", request=mock_response.request, response=mock_response)
    response = client.post("/comments/12345/like")
    assert response.status_code == 400
    assert response.json() == {"detail": "Bad Request"}
    mock_like_object.assert_called_once_with("12345")

@patch("app.meta_api.MetaGraphAPIClient.like_object", new_callable=AsyncMock)
def test_like_comment_generic_error(mock_like_object):
    mock_like_object.side_effect = Exception("Internal Server Error")
    response = client.post("/comments/12345/like")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    mock_like_object.assert_called_once_with("12345")
