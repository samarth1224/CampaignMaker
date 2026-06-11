from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="ADK Server",
    description="API for the Agent Development Kit",
    version="1.0.0"
)

# Optional: Add CORS middleware if you need to access this from a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
