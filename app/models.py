from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CommentRequest(BaseModel):
    message: str = Field(..., description="The content of the comment")

class CommentResponse(BaseModel):
    id: str = Field(..., description="The ID of the created comment")

class LikeResponse(BaseModel):
    success: bool = Field(..., description="Whether the like operation was successful")

class Post(BaseModel):
    id: str
    message: Optional[str] = None
    created_time: str

class PostListResponse(BaseModel):
    data: List[Post]
    paging: Optional[Dict[str, Any]] = None

class Comment(BaseModel):
    id: str
    message: Optional[str] = None
    created_time: str

class CommentListResponse(BaseModel):
    data: List[Comment]
    paging: Optional[Dict[str, Any]] = None
