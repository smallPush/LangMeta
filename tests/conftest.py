import os
import pytest
from app.adapters.meta_api import MetaGraphAPIClient

# Set up required environment variables before any tests run
os.environ["META_ACCESS_TOKEN"] = os.environ.get("META_ACCESS_TOKEN", "test_access_token")
os.environ["META_ACCOUNT_ID"] = os.environ.get("META_ACCOUNT_ID", "test_account_id")
os.environ["META_WEBHOOK_VERIFY_TOKEN"] = os.environ.get("META_WEBHOOK_VERIFY_TOKEN", "your_webhook_verify_token_here")
os.environ["META_APP_SECRET"] = os.environ.get("META_APP_SECRET", "your_meta_app_secret_here")
os.environ["API_KEY"] = os.environ.get("API_KEY", "test_api_key")

@pytest.fixture
def meta_client():
    return MetaGraphAPIClient()
