"""Application-wide configuration — loaded from environment variables."""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── JWT ──────────────────────────────────────────────────────────────────────
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

# ── CORS & Security ──────────────────────────────────────────────────────────
_cors_origins_env = os.getenv("CORS_ORIGINS", '["*"]')
try:
    CORS_ORIGINS: list[str] = json.loads(_cors_origins_env)
except Exception:
    CORS_ORIGINS: list[str] = ["*"]

SECURE_COOKIES: bool = os.getenv("SECURE_COOKIES", "True").lower() in ("true", "1", "yes")

# ── MongoDB ──────────────────────────────────────────────────────────────────
MONGO_URI: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "campaignmaker")

# â”€â”€ Document knowledge base (ChromaDB + Gemini embeddings) â”€â”€â”€â”€â”€â”€
_BACKEND_DIRECTORY = Path(__file__).resolve().parent.parent
CHROMA_PERSIST_DIRECTORY: Path = Path(
    os.getenv("CHROMA_PERSIST_DIRECTORY", str(_BACKEND_DIRECTORY / "data" / "chroma"))
).expanduser()
CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "brand_knowledge")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "gemini-embedding-001")
RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
RAG_EMBEDDING_BATCH_SIZE: int = int(os.getenv("RAG_EMBEDDING_BATCH_SIZE", "50"))
RAG_RETRIEVAL_LIMIT: int = int(os.getenv("RAG_RETRIEVAL_LIMIT", "5"))
RAG_MAX_DOCUMENT_SIZE_MB: int = int(os.getenv("RAG_MAX_DOCUMENT_SIZE_MB", "15"))
RAG_MAX_DOCUMENT_BYTES: int = RAG_MAX_DOCUMENT_SIZE_MB * 1024 * 1024
RAG_MAX_DOCUMENT_CHARACTERS: int = int(
    os.getenv("RAG_MAX_DOCUMENT_CHARACTERS", "300000")
)
RAG_MAX_CHUNKS_PER_DOCUMENT: int = int(
    os.getenv("RAG_MAX_CHUNKS_PER_DOCUMENT", "500")
)
RAG_MAX_FILES_PER_UPLOAD: int = int(os.getenv("RAG_MAX_FILES_PER_UPLOAD", "5"))
RAG_SUPPORTED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt", ".md", ".csv"}
