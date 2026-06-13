from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.router.auth import router as auth_router
from app.router.user import router as user_router
from app.router.agent import router as agent_router
from app.router.campaign import router as campaign_router


# ── Lifespan — runs DB init on startup ───────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="CampaignMaker API",
    description="API for the CampaignMaker AI Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(agent_router)
app.include_router(campaign_router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
