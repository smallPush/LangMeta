from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path, Query, Request, Header
import httpx
import hmac
import hashlib
from typing import Optional
from app.models import (
    CommentRequest,
    CommentResponse,
    LikeResponse,
    PostListResponse,
    CommentListResponse,
    LikeListResponse,
    WebhookPayload
)
from app.meta_api import meta_client
from app.config import settings
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await meta_client.aclose()

app = FastAPI(
    title="Meta Graph API Integration",
    description="A FastAPI project to interact with Meta Graph API for a specific account. Future integration with LangChain.",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(httpx.HTTPStatusError)
async def http_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    return JSONResponse(
        status_code=exc.response.status_code,
        content={"detail": str(exc)},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        # Allow standard FastAPI/Starlette HTTPExceptions to be handled normally
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "ok"}

@app.get("/posts", response_model=PostListResponse, summary="Get account posts")
async def get_posts(limit: int = Query(10, description="Number of posts to retrieve")):
    data = await meta_client.get_posts(limit=limit)
    return data

@app.get("/{object_id}/likes", response_model=LikeListResponse, summary="Get likes for a post or comment")
async def get_likes(
    object_id: str = Path(..., description="The ID of the post or comment"),
    limit: int = Query(10, description="Number of likes to retrieve")
):
    data = await meta_client.get_likes(object_id, limit=limit)
    return data

@app.get("/webhook", summary="Webhook verification endpoint")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token is not None and hmac.compare_digest(hub_verify_token, settings.meta_webhook_verify_token):
        print("Webhook verified successfully!")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook", summary="Webhook notification endpoint")
async def handle_webhook(
    request: Request,
    payload: WebhookPayload,
    x_hub_signature_256: Optional[str] = Header(None)
):
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature")

    # The signature looks like 'sha256=...'
    if not x_hub_signature_256.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Invalid signature format")

    signature = x_hub_signature_256.split("=")[1]

    # Read raw body
    body = await request.body()

    # Calculate HMAC SHA256 signature
    expected_signature = hmac.new(
        settings.meta_app_secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    # Compare signatures
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Log or process the incoming webhook notifications
    print("Received webhook payload:", payload.model_dump())

    # Process Instagram actions like comments, etc.
    if payload.object == "instagram":
        for entry in payload.entry:
            # Add specific logic here based on webhook changes
            pass

    return {"status": "success"}

@app.get("/posts/{post_id}/comments", response_model=CommentListResponse, summary="Get comments for a post")
async def get_comments(
    post_id: str = Path(..., description="The ID of the post"),
    limit: int = Query(10, description="Number of comments to retrieve")
):
    data = await meta_client.get_comments(post_id, limit=limit)
    return data

@app.post("/posts/{post_id}/comments", response_model=CommentResponse, summary="Post a comment on a post")
async def create_comment(
    comment: CommentRequest,
    post_id: str = Path(..., description="The ID of the post to comment on")
):
    data = await meta_client.post_comment(post_id, message=comment.message)
    return data

@app.post("/comments/{comment_id}/like", response_model=LikeResponse, summary="Like a comment")
async def like_comment(
    comment_id: str = Path(..., description="The ID of the comment to like")
):
    data = await meta_client.like_object(comment_id)
    return data
