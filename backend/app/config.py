"""Application-wide configuration — loaded from environment variables."""

import os
import json
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
