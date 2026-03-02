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

@patch("app.meta_api.MetaGraphAPIClient.get_likes", new_callable=AsyncMock)
def test_get_likes_http_status_error(mock_get_likes):
    import httpx

    # Create a mock response for the HTTPStatusError
    mock_response = httpx.Response(status_code=400, request=httpx.Request("GET", "https://example.com"))

    # Configure the mock to raise HTTPStatusError
    mock_get_likes.side_effect = httpx.HTTPStatusError("Bad Request", request=mock_response.request, response=mock_response)

    response = client.get("/test_object_id/likes")

    assert response.status_code == 400
    assert response.json() == {"detail": "Bad Request"}
