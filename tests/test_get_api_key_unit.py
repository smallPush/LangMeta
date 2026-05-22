import pytest
from fastapi import HTTPException
from app.main import get_api_key
from app.config import settings

@pytest.mark.asyncio
async def test_get_api_key_valid_header():
    """Verify that a valid header API key is accepted."""
    settings.api_key = "secure_key"
    result = await get_api_key(api_key_header="secure_key")
    assert result == "secure_key"

@pytest.mark.asyncio
async def test_get_api_key_invalid_header():
    """Verify that an invalid header API key raises 403."""
    settings.api_key = "secure_key"
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key(api_key_header="wrong_key")
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate API Key"

@pytest.mark.asyncio
async def test_get_api_key_missing():
    """Verify that missing header API key raises 403."""
    settings.api_key = "secure_key"
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key(api_key_header=None)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate API Key"
