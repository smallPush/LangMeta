import os
import pytest
from fastapi.testclient import TestClient

# Set up environment variables for config validation
os.environ["META_ACCESS_TOKEN"] = "test"
os.environ["META_ACCOUNT_ID"] = "test"
os.environ["META_WEBHOOK_VERIFY_TOKEN"] = "test"
os.environ["META_APP_SECRET"] = "test"
# In test_security.py, we override API_KEY but since app.main might be imported before this,
# we should make sure we're testing against the actual settings.api_key.
os.environ["API_KEY"] = "secure_key"

from app.main import app
from app.config import settings
settings.api_key = "secure_key"

client = TestClient(app)

def test_logs_inaccessible_without_auth():
    """Verify that /logs is NOT accessible without authentication."""
    response = client.get("/logs")
    assert response.status_code == 403

def test_logs_ui_inaccessible_without_auth():
    """Verify that /logs/ui is NOT accessible without authentication."""
    response = client.get("/logs/ui")
    assert response.status_code == 403

def test_logs_accessible_with_header(monkeypatch):
    """Verify that /logs is accessible with the correct X-API-Key header."""
    from app.config import settings
    from app.main import api_logger
    api_logger.clear_logs()
    monkeypatch.setattr(settings, "api_key", "secure_key")
    response = client.get("/logs", headers={"X-API-Key": "secure_key"})
    assert response.status_code == 200

def test_logs_ui_accessible_with_query_param(monkeypatch):
    """Verify that /logs/ui is accessible with the correct api_key query parameter."""
    from app.config import settings
    from app.main import api_logger
    api_logger.clear_logs()
    monkeypatch.setattr(settings, "api_key", "secure_key")
    response = client.get("/logs/ui?api_key=secure_key")
    assert response.status_code == 200

def test_logs_inaccessible_with_wrong_key(monkeypatch):
    """Verify that /logs returns 403 with an incorrect API Key."""
    from app.config import settings
    monkeypatch.setattr(settings, "api_key", "secure_key")
    response = client.get("/logs", headers={"X-API-Key": "wrong_key"})
    assert response.status_code == 403
