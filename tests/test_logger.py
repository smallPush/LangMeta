import os

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.logger_service import api_logger

settings.api_key = "test_api_key"

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
