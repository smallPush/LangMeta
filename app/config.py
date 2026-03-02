from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    meta_access_token: str
    meta_account_id: str
    meta_api_version: str = "v19.0"
    meta_webhook_verify_token: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
