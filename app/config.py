from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    meta_access_token: str = "your_meta_access_token_here"
    meta_account_id: str = "your_meta_account_id_here"
    meta_api_version: str = "v19.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
