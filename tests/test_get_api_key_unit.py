import pytest
from fastapi import HTTPException
from app.main import get_api_key
from app.config import settings

@pytest.mark.asyncio
async def test_get_api_key_valid_header():
    """Verify that a valid header API key is accepted."""
    settings.api_key = "secure_key"
    result = await get_api_key(api_key_header="secure_key", api_key_query=None)
    assert result == "secure_key"

@pytest.mark.asyncio
async def test_get_api_key_valid_query():
    """Verify that a valid query API key is accepted."""
    settings.api_key = "secure_key"
    result = await get_api_key(api_key_header=None, api_key_query="secure_key")
    assert result == "secure_key"

@pytest.mark.asyncio
async def test_get_api_key_invalid_header():
    """Verify that an invalid header API key raises 403."""
    settings.api_key = "secure_key"
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key(api_key_header="wrong_key", api_key_query=None)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate API Key"

@pytest.mark.asyncio
async def test_get_api_key_invalid_query():
    """Verify that an invalid query API key raises 403."""
    settings.api_key = "secure_key"
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key(api_key_header=None, api_key_query="wrong_key")
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate API Key"

@pytest.mark.asyncio
async def test_get_api_key_missing_both():
    """Verify that missing both header and query API key raises 403."""
    settings.api_key = "secure_key"
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key(api_key_header=None, api_key_query=None)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate API Key"

@pytest.mark.asyncio
async def test_get_api_key_valid_header_invalid_query():
    """Verify that a valid header API key and an invalid query API key is accepted."""
    settings.api_key = "secure_key"
    result = await get_api_key(api_key_header="secure_key", api_key_query="wrong_key")
    assert result == "secure_key"

@pytest.mark.asyncio
async def test_get_api_key_invalid_header_valid_query():
    """Verify that an invalid header API key and a valid query API key is accepted."""
    settings.api_key = "secure_key"
    result = await get_api_key(api_key_header="wrong_key", api_key_query="secure_key")
    assert result == "secure_key"
