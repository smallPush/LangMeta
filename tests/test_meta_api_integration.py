import pytest

from app.adapters.meta_api import MetaGraphAPIClient
from app.config import settings


# Skip these tests unless explicitly requested or if we have a real token
# We check if META_ACCESS_TOKEN and META_ACCOUNT_ID are not the default/placeholder ones
def is_real_config():
    """Test function docstring."""
    return (
        settings.meta_access_token 
        and settings.meta_access_token != "test_access_token"
        and settings.meta_account_id 
        and settings.meta_account_id != "test_account_id"
    )

pytestmark = pytest.mark.skipif(
    not is_real_config(),
    reason="META_ACCESS_TOKEN or META_ACCOUNT_ID not configured for integration tests"
)

@pytest.fixture
async def real_meta_client():
    """Test function docstring."""
    client = MetaGraphAPIClient()
    yield client
    await client.aclose()

@pytest.mark.asyncio
async def test_real_get_posts(real_meta_client):
    """Test fetching posts from a real Meta account."""
    result = await real_meta_client.get_posts(limit=1)
    assert "data" in result
    assert isinstance(result["data"], list)

@pytest.mark.asyncio
async def test_real_get_comments_on_first_post(real_meta_client):
    """Test fetching comments for the most recent post."""
    posts = await real_meta_client.get_posts(limit=1)
    if not posts["data"]:
        pytest.skip("No posts found to test comments on.")
    
    post_id = posts["data"][0]["id"]
    result = await real_meta_client.get_comments(post_id, limit=1)
    assert "data" in result
    assert isinstance(result["data"], list)

@pytest.mark.asyncio
async def test_real_get_likes_on_first_post(real_meta_client):
    """Test fetching likes for the most recent post."""
    posts = await real_meta_client.get_posts(limit=1)
    if not posts["data"]:
        pytest.skip("No posts found to test likes on.")
    
    post_id = posts["data"][0]["id"]
    result = await real_meta_client.get_likes(post_id, limit=1)
    assert "data" in result
    assert isinstance(result["data"], list)
