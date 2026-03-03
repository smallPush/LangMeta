from abc import ABC, abstractmethod
from typing import Dict, Any

class SocialMediaPort(ABC):
    @abstractmethod
    async def aclose(self):
        """Close the underlying resources if any."""
        pass

    @abstractmethod
    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        """Fetch posts."""
        pass

    @abstractmethod
    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        """Fetch comments for a specific post."""
        pass

    @abstractmethod
    async def post_comment(self, object_id: str, message: str) -> Dict[str, Any]:
        """Post a comment on a specific object."""
        pass

    @abstractmethod
    async def like_object(self, object_id: str) -> Dict[str, Any]:
        """Like a specific object."""
        pass

    @abstractmethod
    async def get_likes(self, object_id: str, limit: int = 10) -> Dict[str, Any]:
        """Fetch likes for a specific object."""
        pass
