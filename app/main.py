from fastapi import FastAPI, HTTPException, Path, Query
import httpx
from app.models import (
    CommentRequest,
    CommentResponse,
    LikeResponse,
    PostListResponse,
    CommentListResponse
)
from app.meta_api import meta_client

app = FastAPI(
    title="Meta Graph API Integration",
    description="A FastAPI project to interact with Meta Graph API for a specific account. Future integration with LangChain.",
    version="1.0.0"
)

@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "ok"}

@app.get("/posts", response_model=PostListResponse, summary="Get account posts")
async def get_posts(limit: int = Query(10, description="Number of posts to retrieve")):
    try:
        data = await meta_client.get_posts(limit=limit)
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/{post_id}/comments", response_model=CommentListResponse, summary="Get comments for a post")
async def get_comments(
    post_id: str = Path(..., description="The ID of the post"),
    limit: int = Query(10, description="Number of comments to retrieve")
):
    try:
        data = await meta_client.get_comments(post_id, limit=limit)
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/{post_id}/comments", response_model=CommentResponse, summary="Post a comment on a post")
async def create_comment(
    comment: CommentRequest,
    post_id: str = Path(..., description="The ID of the post to comment on")
):
    try:
        data = await meta_client.post_comment(post_id, message=comment.message)
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/comments/{comment_id}/like", response_model=LikeResponse, summary="Like a comment")
async def like_comment(
    comment_id: str = Path(..., description="The ID of the comment to like")
):
    try:
        data = await meta_client.like_object(comment_id)
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
