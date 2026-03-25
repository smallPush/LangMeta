from typing import Any


class ExternalAPIError(Exception):
    """Exception raised when an external API request fails."""
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"External API Error {status_code}: {detail}")
