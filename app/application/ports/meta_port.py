from abc import ABC, abstractmethod
from typing import Dict, Any

class MetaPort(ABC):
    @abstractmethod
    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def post_comment(self, object_id: str, message: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def like_object(self, object_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_likes(self, object_id: str, limit: int = 10) -> Dict[str, Any]:
        pass
