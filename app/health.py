# File: app/health.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    """Used by Docker/K8s healthchecks."""
    return JSONResponse(content={"status": "ok"})