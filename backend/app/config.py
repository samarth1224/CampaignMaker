"""Application-wide configuration — loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── JWT ──────────────────────────────────────────────────────────────────────
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

# ── MongoDB ──────────────────────────────────────────────────────────────────
MONGO_URI: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "campaignmaker")
