import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-sonnet-4-20250514")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    VECTOR_STORE_DIR: str = os.getenv("VECTOR_STORE_DIR", "data/vectorstore")


settings = Settings()
