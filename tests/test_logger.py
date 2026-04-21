from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
settings.api_key = "test_api_key"
from app.services.logger_service import api_logger
import pytest

client = TestClient(app, raise_server_exceptions=False)

@pytest.fixture(autouse=True)
def clear_logs_before_test():
    api_logger.clear_logs()
    yield

def test_logger_middleware_incoming():
    response = client.get("/health")
    assert response.status_code == 200

    logs = api_logger.get_logs()
    assert len(logs) == 1
    assert logs[0]["type"] == "incoming"
    assert logs[0]["method"] == "GET"
    assert logs[0]["url"] == "/health"
    assert logs[0]["status_code"] == 200

def test_logger_get_logs_endpoint():
    api_logger.clear_logs()
    # Make a request to generate a log
    client.get("/health")

    response = client.get("/logs", headers={"X-API-Key": settings.api_key})
    assert response.status_code == 200

    data = response.json()
    assert "logs" in data
    # The first request (/health) + the request to (/logs) will be logged
    # However, since we're calling /logs, the incoming log for /logs might be added *after* the handler logic,
    # but the /health log will definitely be there.
    assert len(data["logs"]) >= 1
    assert data["logs"][0]["url"] == "/health"

def test_logger_ui_endpoint():
    api_logger.clear_logs()
    response = client.get(f"/logs/ui?api_key={settings.api_key}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "API Call Logs" in response.text

def test_log_webhook_event():
    api_logger.clear_logs()
    payload = {"test": "payload"}
    api_logger.log_webhook_event("POST", "/webhook", 200, "payload", payload=payload)

    logs = api_logger.get_logs()
    assert len(logs) == 1
    assert logs[0]["type"] == "webhook"
    assert logs[0]["method"] == "POST"
    assert logs[0]["url"] == "/webhook"
    assert logs[0]["status_code"] == 200
    assert logs[0]["event_type"] == "payload"
    assert logs[0]["payload"] == payload

def test_logger_maxlen():
    from app.services.logger_service import APILogger
    logger = APILogger(maxlen=2)
    logger.log_call("incoming", "GET", "/test1", 200, 10.0)
    logger.log_call("incoming", "GET", "/test2", 200, 10.0)
    logger.log_call("incoming", "GET", "/test3", 200, 10.0)

    logs = logger.get_logs()
    assert len(logs) == 2
    assert logs[0]["url"] == "/test2"
    assert logs[1]["url"] == "/test3"
