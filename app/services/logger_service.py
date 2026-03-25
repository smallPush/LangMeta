import time
from threading import Lock
from typing import Any, Dict, List


class APILogger:
    def __init__(self, maxlen: int = 1000):
        self.logs: List[Dict[str, Any]] = []
        self.maxlen = maxlen
        self._lock = Lock()

    def log_call(self, call_type: str, method: str, url: str, status_code: int, response_time_ms: float, error: str = None):
        """
        Log an API call.
        call_type: "incoming" or "outgoing"
        """
        log_entry = {
            "timestamp": time.time(),
            "type": call_type,
            "method": method,
            "url": str(url),
            "status_code": status_code,
            "response_time_ms": response_time_ms,
        }
        if error is not None:
            log_entry["error"] = error

        with self._lock:
            self.logs.append(log_entry)
            if len(self.logs) > self.maxlen:
                self.logs.pop(0)

    def get_logs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return self.logs[:]

    def clear_logs(self):
        with self._lock:
            self.logs.clear()

# Global singleton instance
api_logger = APILogger()
