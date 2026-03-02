from fastapi.testclient import TestClient
from app.main import app
import httpx
from unittest.mock import patch, AsyncMock, MagicMock

client = TestClient(app)

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
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

@patch("app.meta_api.MetaGraphAPIClient.get_likes", new_callable=AsyncMock)
def test_get_likes(mock_get_likes):
    mock_get_likes.return_value = {"data": [{"id": "123", "name": "Test User"}]}
    response = client.get("/test_object_id/likes")
    assert response.status_code == 200
    assert response.json() == {"data": [{"id": "123", "name": "Test User"}], "paging": None}

@patch("app.meta_api.MetaGraphAPIClient.post_comment", new_callable=AsyncMock)
def test_create_comment_success(mock_post_comment):
    mock_post_comment.return_value = {"id": "12345"}
    response = client.post("/posts/post123/comments", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json() == {"id": "12345"}

@patch("app.meta_api.MetaGraphAPIClient.post_comment", new_callable=AsyncMock)
def test_create_comment_http_error(mock_post_comment):
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 400
    mock_post_comment.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
    response = client.post("/posts/post123/comments", json={"message": "Hello"})
    assert response.status_code == 400

@patch("app.meta_api.MetaGraphAPIClient.post_comment", new_callable=AsyncMock)
def test_create_comment_generic_error(mock_post_comment):
    mock_post_comment.side_effect = Exception("Generic error")
    response = client.post("/posts/post123/comments", json={"message": "Hello"})
    assert response.status_code == 500

@patch("app.meta_api.MetaGraphAPIClient.get_posts", new_callable=AsyncMock)
def test_get_posts(mock_get_posts):
    mock_get_posts.return_value = {"data": [{"id": "p1", "message": "msg", "created_time": "2023-01-01T00:00:00+0000"}]}
    response = client.get("/posts")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1

@patch("app.meta_api.MetaGraphAPIClient.get_comments", new_callable=AsyncMock)
def test_get_comments(mock_get_comments):
    mock_get_comments.return_value = {"data": [{"id": "c1", "message": "msg", "created_time": "2023-01-01T00:00:00+0000"}]}
    response = client.get("/posts/post123/comments")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1

@patch("app.meta_api.MetaGraphAPIClient.like_object", new_callable=AsyncMock)
def test_like_comment(mock_like_object):
    mock_like_object.return_value = {"success": True}
    response = client.post("/comments/comm123/like")
    assert response.status_code == 200
    assert response.json() == {"success": True}
