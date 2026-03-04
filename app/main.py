from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path, Query, Request, Header
import httpx
import hmac
import hashlib
from typing import Optional
from app.domain.models import (
    CommentRequest,
    CommentResponse,
    LikeResponse,
    PostListResponse,
    CommentListResponse,
    LikeListResponse,
    WebhookPayload
)
from app.adapters.meta_api import MetaGraphAPIClient
from app.services.social_media_service import SocialMediaService
from app.config import settings
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from app.services.logger_service import api_logger

meta_client = MetaGraphAPIClient()
social_media_service = SocialMediaService(meta_client)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Nothing to do, client is lazily initialized
    yield
    # Shutdown: Close the meta_client
    await social_media_service.aclose()

app = FastAPI(
    title="Meta Graph API Integration",
    description="A FastAPI project to interact with Meta Graph API for a specific account. Future integration with LangChain.",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000
        api_logger.log_call(
            call_type="incoming",
            method=request.method,
            url=str(request.url.path),
            status_code=response.status_code,
            response_time_ms=process_time_ms
        )
        return response
    except Exception as exc:
        process_time_ms = (time.time() - start_time) * 1000
        api_logger.log_call(
            call_type="incoming",
            method=request.method,
            url=str(request.url.path),
            status_code=500,
            response_time_ms=process_time_ms,
            error=str(exc)
        )
        raise exc

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

@app.get("/logs", summary="Get API call logs")
async def get_logs():
    return {"logs": api_logger.get_logs()}

@app.get("/logs/ui", response_class=HTMLResponse, summary="UI to view API call logs")
async def logs_ui():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Call Logs</title>
        <style>
            body { font-family: sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .incoming { color: blue; }
            .outgoing { color: green; }
            .error { color: red; }
            h1 { font-size: 24px; }
            button { padding: 10px; margin-bottom: 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>API Call Logs</h1>
        <button onclick="fetchLogs()">Refresh Logs</button>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Type</th>
                    <th>Method</th>
                    <th>URL</th>
                    <th>Status</th>
                    <th>Time (ms)</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody id="logs-body">
                <tr><td colspan="7">Loading logs...</td></tr>
            </tbody>
        </table>
        <script>
            async function fetchLogs() {
                try {
                    const response = await fetch('/logs');
                    const data = await response.json();
                    const logs = data.logs;
                    const tbody = document.getElementById('logs-body');
                    tbody.innerHTML = '';

                    if (logs.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="7">No logs available.</td></tr>';
                        return;
                    }

                    // Function to escape HTML to prevent XSS
                    function escapeHtml(unsafe) {
                        if (!unsafe) return '';
                        return unsafe
                             .toString()
                             .replace(/&/g, "&amp;")
                             .replace(/</g, "&lt;")
                             .replace(/>/g, "&gt;")
                             .replace(/"/g, "&quot;")
                             .replace(/'/g, "&#039;");
                    }

                    // Reverse logs to show newest first
                    logs.reverse().forEach(log => {
                        const tr = document.createElement('tr');
                        const date = new Date(log.timestamp * 1000).toISOString();
                        const typeClass = log.type === 'incoming' ? 'incoming' : 'outgoing';
                        const statusClass = (log.status_code >= 400 || log.error) ? 'error' : '';

                        tr.innerHTML = `
                            <td>${escapeHtml(date)}</td>
                            <td class="${typeClass}"><b>${escapeHtml(log.type.toUpperCase())}</b></td>
                            <td>${escapeHtml(log.method)}</td>
                            <td>${escapeHtml(log.url)}</td>
                            <td class="${statusClass}">${escapeHtml(log.status_code)}</td>
                            <td>${escapeHtml(log.response_time_ms.toFixed(2))}</td>
                            <td class="${statusClass}">${escapeHtml(log.error)}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                } catch (error) {
                    console.error('Error fetching logs:', error);
                    document.getElementById('logs-body').innerHTML = '<tr><td colspan="7" class="error">Error loading logs.</td></tr>';
                }
            }
            // Initial fetch
            fetchLogs();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/posts", response_model=PostListResponse, summary="Get account posts")
async def get_posts(limit: int = Query(10, description="Number of posts to retrieve")):
    data = await social_media_service.get_posts(limit=limit)
    return data

@app.get("/{object_id}/likes", response_model=LikeListResponse, summary="Get likes for a post or comment")
async def get_likes(
    object_id: str = Path(..., description="The ID of the post or comment"),
    limit: int = Query(10, description="Number of likes to retrieve")
):
    data = await social_media_service.get_likes(object_id, limit=limit)
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
    data = await social_media_service.get_comments(post_id, limit=limit)
    return data

@app.post("/posts/{post_id}/comments", response_model=CommentResponse, summary="Post a comment on a post")
async def create_comment(
    comment: CommentRequest,
    post_id: str = Path(..., description="The ID of the post to comment on")
):
    data = await social_media_service.post_comment(post_id, message=comment.message)
    return data

@app.post("/comments/{comment_id}/like", response_model=LikeResponse, summary="Like a comment")
async def like_comment(
    comment_id: str = Path(..., description="The ID of the comment to like")
):
    data = await social_media_service.like_object(comment_id)
    return data
