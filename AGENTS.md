# AGENTS.md

## Commands
- Install app runtime deps with `pip install -r requirements.txt`; install test/CI-only tools separately with `pip install pytest pytest-asyncio pylint`.
- Run the app locally with `uvicorn app.main:app --reload`; Docker uses `uvicorn app.main:app --host 0.0.0.0 --port 8000` via `docker-compose up --build`.
- Run tests with `PYTHONPATH=. python3 -m pytest tests/`; run one file or test as `PYTHONPATH=. python3 -m pytest tests/test_api.py::test_health_check`.
- Match CI linting with `pylint --disable=C,R,W $(git ls-files '*.py')` after installing the CI tools.

## Configuration
- `app.config.settings` is instantiated at import time and requires `META_ACCESS_TOKEN`, `META_ACCOUNT_ID`, `META_WEBHOOK_VERIFY_TOKEN`, `META_APP_SECRET`, and `API_KEY`; use `.env` or set env vars before importing app modules in scripts.
- `tests/conftest.py` supplies placeholder env vars for pytest, but ad hoc imports of `app.config` outside pytest will fail without config.
- Real Meta integration tests in `tests/test_meta_api_integration.py` auto-skip unless `META_ACCESS_TOKEN` and `META_ACCOUNT_ID` are non-placeholder values.

## Architecture Notes
- FastAPI entrypoint is `app/main.py`; global `http_client`, `MetaGraphAPIClient`, and `SocialMediaService` instances are created at import time and closed in the lifespan handler.
- The code follows ports/adapters: route handlers call `app.services.social_media_service.SocialMediaService`, which delegates to `app.ports.social_media.SocialMediaPort`; Meta HTTP behavior lives in `app/adapters/meta_api.py`.
- Protected API routes require the `X-API-Key` header; `/health` and `/webhook` are intentionally unprotected.
- `cron.py` is a standalone async job that fetches posts through the same Meta adapter/service and processes comments concurrently with a semaphore.

## Testing Gotchas
- For route tests, patch the object actually used by `app.main` when possible, e.g. `app.main.social_media_service.get_likes`, because service/client singletons already exist after `app.main` import.
- Webhook POST tests must sign the exact raw body with `settings.meta_app_secret`; parsing happens only after signature validation.
- Mock Meta responses should follow the shapes in `mocks/*.json` and `app/domain/models.py` (`data` arrays plus optional `paging`).
