from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    documents_storage_path: Path = Path("./data/documents")
    groq_api_key: str | None = None
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

settings = Settings()