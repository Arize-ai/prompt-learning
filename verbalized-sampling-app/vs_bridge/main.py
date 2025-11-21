"""
FastAPI sidecar service for Verbalized Sampling Desktop App

This service wraps the verbalized_sampling package and provides
HTTP endpoints for the Tauri Rust backend to communicate with.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# For PyInstaller: try relative import, fallback to absolute
try:
    from . import models
except ImportError:
    import vs_bridge.models as models

# Create FastAPI application
app = FastAPI(
    title="Verbalized Sampling Sidecar",
    description="Python sidecar service for LLM sampling distribution visualization",
    version="0.1.0"
)

# Configure CORS for Tauri webview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],  # Tauri dev and production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for sidecar lifecycle management"""
    return {"status": "ok", "version": "0.1.0"}

@app.post("/api/v1/verbalize")
async def verbalize(request: models.VerbRequest) -> models.VerbResponse:
    """
    Verbalize endpoint - Generate k weighted completions

    Creates a probability distribution over k LLM completions
    with temperature scaling and normalization.
    """
    # For PyInstaller: try relative import, fallback to absolute
    try:
        from .handlers.verbalize import verbalization_service
    except ImportError:
        from vs_bridge.handlers.verbalize import verbalization_service

    return await verbalization_service.verbalize(request)

@app.post("/api/v1/sample")
async def sample():
    """Sample endpoint - to be implemented in Phase 4"""
    return {"message": "Sample endpoint - Phase 4"}

@app.post("/api/v1/export")
async def export():
    """Export endpoint - to be implemented in Phase 7"""
    return {"message": "Export endpoint - Phase 7"}

@app.post("/api/v1/session/save")
async def save_session():
    """Session save endpoint - to be implemented in Phase 6"""
    return {"message": "Session save - Phase 6"}

@app.post("/api/v1/session/load")
async def load_session():
    """Session load endpoint - to be implemented in Phase 6"""
    return {"message": "Session load - Phase 6"}

if __name__ == "__main__":
    # Run FastAPI server on localhost:8765
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8765,
        log_level="info"
    )
