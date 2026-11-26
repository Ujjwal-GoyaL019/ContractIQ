from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(ROOT_DIR, "inventory_risk.db").replace(os.sep, "/")
DEFAULT_QDRANT_PATH = os.path.join(ROOT_DIR, "qdrant_storage")


class Settings(BaseSettings):
    APP_NAME: str = "ContractIQ - Smart Supplier & Risk Advisor"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-change-in-production"

    # Database (Defaults to consistent project root path)
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"

    # Qdrant Vector DB
    QDRANT_URL: str = DEFAULT_QDRANT_PATH
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "supplier_documents"

    # Embedding Model
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"

    # Groq LLM
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
