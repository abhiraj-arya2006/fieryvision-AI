from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine, Base
from app.api.router import router as api_router

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FieryVision AI Backend",
    description="Early industrial fire risk detection and satellite intelligence backend for Giaspura, Ludhiana, Punjab.",
    version="1.0.0"
)

# Configure CORS for frontend access
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router under /api
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "service": "FieryVision AI Backend API",
        "status": "online",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
