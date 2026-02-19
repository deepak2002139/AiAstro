"""
Configuration management for Astrology RAG Service
Handles environment variables and application settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
CHROMA_DB_PATH = BASE_DIR / "chroma_db"
LOGS_DIR = BASE_DIR / "logs"
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base.md"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
CHROMA_DB_PATH.mkdir(exist_ok=True)


class Settings:
    """Application settings from environment variables."""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))

    # Vector Store Configuration
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "astrology_kb")

    # RAG Configuration
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", "400"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "5"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # Agentic RAG Configuration
    MAX_SEARCH_ROUNDS = int(os.getenv("MAX_SEARCH_ROUNDS", "3"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"

    @classmethod
    def validate(cls):
        """Validate that all required settings are configured."""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")

        if not KNOWLEDGE_BASE_PATH.exists():
            errors.append(f"Knowledge base not found at {KNOWLEDGE_BASE_PATH}")

        return len(errors) == 0, errors

    @classmethod
    def get_summary(cls):
        """Get a summary of all settings (excluding API key)."""
        return {
            "openai_model": cls.OPENAI_MODEL,
            "embedding_model": cls.OPENAI_EMBEDDING_MODEL,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
            "chroma_db": str(CHROMA_DB_PATH),
            "knowledge_base": str(KNOWLEDGE_BASE_PATH),
            "max_chunk_size": cls.MAX_CHUNK_SIZE,
            "retrieval_k": cls.RETRIEVAL_K,
        }


settings = Settings()

