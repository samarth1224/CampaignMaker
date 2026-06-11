"""Database initialisation — connects Motor to MongoDB and inits Beanie."""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app import config
from app.models.usermodel import User
from app.models.campaign import Campaign


async def init_db() -> None:
    """Create the Motor client and initialise Beanie with all documents.

    Call this once at application startup (e.g. in a ``lifespan`` or
    ``on_event("startup")`` handler).
    """
    client = AsyncIOMotorClient(config.MONGO_URI)
    await init_beanie(
        database=client[config.MONGO_DB_NAME],
        document_models=[User, Campaign],
    )
