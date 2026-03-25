from unittest.mock import patch, AsyncMock

import pytest

from cron import fetch_and_process, process_comment

@pytest.mark.asyncio
@patch("app.services.social_media_service.SocialMediaService.get_posts", new_callable=AsyncMock)
@patch("app.services.social_media_service.SocialMediaService.get_likes", new_callable=AsyncMock)
@patch("app.services.social_media_service.SocialMediaService.get_comments", new_callable=AsyncMock)
@patch("builtins.print")
async def test_fetch_and_process_success(mock_print, mock_get_comments, mock_get_likes, mock_get_posts):
    # Setup mock returns
    mock_get_posts.return_value = {
        "data": [
            {"id": "post_1"}
        ]
    }

    # get_likes is called for post only now
    # We can use side_effect or just return a static list for all calls
    # Let's provide likes for post_1
    mock_get_likes.side_effect = [
        {"data": [{"id": "like_1"}, {"id": "like_2"}]}, # likes for post_1
    ]

    mock_get_comments.return_value = {
        "data": [
            {"id": "comment_1", "likes": {"data": [{"id": "like_3"}]}}
        ]
    }

    # Execute the function
    await fetch_and_process()

    # Assert get_posts was called
    mock_get_posts.assert_called_once_with(limit=5)

    # Assert get_likes was called correctly
    # 1. For the post only
    assert mock_get_likes.call_count == 1
    mock_get_likes.assert_any_call("post_1", limit=5)

    # Assert get_comments was called correctly
    mock_get_comments.assert_called_once_with("post_1", limit=5)

    # Assert output
    mock_print.assert_any_call("Running cron job to fetch posts, comments, and likes...")
    mock_print.assert_any_call("Processing post: post_1")
    mock_print.assert_any_call("  Post post_1 has 2 likes.")
    mock_print.assert_any_call("  Processing comment: comment_1")
    mock_print.assert_any_call("    Comment comment_1 has 1 likes.")

@pytest.mark.asyncio
@patch("app.services.social_media_service.SocialMediaService.get_posts", new_callable=AsyncMock)
@patch("builtins.print")
async def test_fetch_and_process_exception(mock_print, mock_get_posts):
    # Setup mock to raise exception
    mock_get_posts.side_effect = Exception("Test exception")

    # Execute the function
    await fetch_and_process()

    # Assert output caught exception
    mock_print.assert_any_call("Running cron job to fetch posts, comments, and likes...")
    mock_print.assert_any_call("An error occurred during cron execution: Test exception")

@pytest.mark.asyncio
@patch("builtins.print")
async def test_process_comment_success(mock_print):
    mock_service = AsyncMock()

    comment = {
        "id": "comment_123",
        "likes": {
            "data": [{"id": "like_1"}, {"id": "like_2"}]
        }
    }
    await process_comment(mock_service, comment)

    mock_print.assert_any_call("  Processing comment: comment_123")
    mock_print.assert_any_call("    Comment comment_123 has 2 likes.")

@pytest.mark.asyncio
@patch("builtins.print")
async def test_process_comment_no_likes(mock_print):
    mock_service = AsyncMock()

    comment = {"id": "comment_456"}
    await process_comment(mock_service, comment)

    mock_print.assert_any_call("  Processing comment: comment_456")
    mock_print.assert_any_call("    Comment comment_456 has 0 likes.")
