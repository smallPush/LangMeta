import time
import collections
import threading
from typing import List, Dict, Any, Deque

class APILogger:
    def __init__(self, maxlen: int = 1000):
        self.logs: Deque[Dict[str, Any]] = collections.deque(maxlen=maxlen)
        self.maxlen = maxlen
        self.lock = threading.Lock()

    def _add_log(self, log_entry: Dict[str, Any]):
        with self.lock:
            self.logs.append(log_entry)

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

        self._add_log(log_entry)

    def log_webhook_event(self, method: str, url: str, status_code: int, event_type: str, payload: Dict[str, Any] = None):
        """
        Log a webhook event.
        event_type: "verification" or "payload"
        """
        log_entry = {
            "timestamp": time.time(),
            "type": "webhook",
            "method": method,
            "url": str(url),
            "status_code": status_code,
            "response_time_ms": 0.0,
            "event_type": event_type,
        }
        if payload is not None:
            log_entry["payload"] = payload

        self._add_log(log_entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.logs)

    def clear_logs(self):
        with self.lock:
            self.logs.clear()

# Global singleton instance
api_logger = APILogger()
