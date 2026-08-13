# File: app/main.py
import logging
from fastapi import FastAPI, HTTPException, Depends, Path
from pydantic import BaseModel, Field
from typing import List, Optional
import requests
from .config import settings
from .github import (
    list_releases,
    get_release,
    create_release,
    delete_release,
)
from .health import router as health_router

# Logging configuration
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Release Manager",
    version="1.0.0",
    description="Production‑ready FastAPI wrapper around the GitHub Releases API."
)

# Register health endpoint
app.include_router(health_router)

# --------------------------- Pydantic models ---------------------------

class ReleaseCreatePayload(BaseModel):
    repo: str = Field(..., description="Repository name (e.g., `my-app`).")
    tag_name: str = Field(..., description="Tag name (e.g., `v1.0.0`).")
    name: Optional[str] = Field(None, description="Human‑readable release name.")
    body: Optional[str] = Field(None, description="Release notes.")
    draft: bool = Field(False, description="Mark as draft.")
    prerelease: bool = Field(False, description="Mark as prerelease.")
    target_commitish: Optional[str] = Field(
        None, description="Commitish for the tag (defaults to default branch)."
    )

class ReleaseResponse(BaseModel):
    id: int
    tag_name: str
    name: Optional[str]
    body: Optional[str]
    draft: bool
    prerelease: bool
    html_url: str
    created_at: str
    published_at: Optional[str]

# --------------------------- Dependency ---------------------------

def verify_org(org: str = Path(..., description="GitHub organization/user")):
    """Only allow the org configured in .env."""
    if org != settings.GITHUB_ORG:
        raise HTTPException(status_code=403, detail="Forbidden organization")
    return org

# --------------------------- API endpoints ---------------------------

@app.get(
    "/orgs/{org}/repos/{repo}/releases",
    response_model=List[ReleaseResponse],
    summary="List all releases for a repository"
)
def api_list_releases(
    org: str = Depends(verify_org),
    repo: str = Path(..., description="Repository name")
):
    try:
        releases = list_releases(repo)
        return [ReleaseResponse(**r) for r in releases]
    except Exception as exc:
        logger.exception("Error listing releases")
        raise HTTPException(status_code=502, detail=str(exc))

@app.get(
    "/orgs/{org}/repos/{repo}/releases/{release_id}",
    response_model=ReleaseResponse,
    summary="Get a single release"
)
def api_get_release(
    org: str = Depends(verify_org),
    repo: str = Path(..., description="Repository name"),
    release_id: int = Path(..., description="Release numeric ID")
):
    try:
        release = get_release(repo, release_id)
        return ReleaseResponse(**release)
    except requests.HTTPError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Release not found")
        raise HTTPException(status_code=502, detail=str(exc))

@app.post(
    "/orgs/{org}/repos/{repo}/releases",
    response_model=ReleaseResponse,
    status_code=201,
    summary="Create a new release"
)
def api_create_release(
    payload: ReleaseCreatePayload,
    org: str = Depends(verify_org)
):
    try:
        release = create_release(
            repo=payload.repo,
            tag_name=payload.tag_name,
            name=payload.name,
            body=payload.body,
            draft=payload.draft,
            prerelease=payload.prerelease,
            target_commitish=payload.target_commitish,
        )
        return ReleaseResponse(**release)
    except requests.HTTPError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

@app.delete(
    "/orgs/{org}/repos/{repo}/releases/{release_id}",
    status_code=204,
    summary="Delete a release"
)
def api_delete_release(
    org: str = Depends(verify_org),
    repo: str = Path(..., description="Repository name"),
    release_id: int = Path(..., description="Release numeric ID")
):
    try:
        delete_release(repo, release_id)
    except requests.HTTPError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Release not found")
        raise HTTPException(status_code=502, detail=str(exc))
    return

# ----------------------------------------------------------------------
# Miscellaneous utility endpoints
# ----------------------------------------------------------------------
@app.get("/", tags=["Root"])
def root() -> dict:
    """Simple root endpoint."""
    return {
        "message": "GitHub Release Manager API",
        "documentation": "/docs",
        "status": "ready"
    }

@app.get("/version", tags=["Info"])
def version_info() -> dict:
    """Return app version and (if reachable) GitHub API version."""
    github_version = None
    try:
        resp = requests.get(f"{settings.GITHUB_API_URL}/meta", headers=_headers())
        if resp.status_code == 200:
            github_version = resp.json().get("github_services_sha")
    except Exception:
        github_version = None
    return {
        "app_version": "1.0.0",
        "github_api_version": github_version,
    }

# ----------------------------------------------------------------------
# Global exception handler for requests.HTTPError
# ----------------------------------------------------------------------
@app.exception_handler(requests.HTTPError)
def http_error_handler(request, exc: requests.HTTPError):
    logger.error("Unhandled requests.HTTPError: %s %s", exc.response.status_code, exc.request.url)
    return JSONResponse(
        status_code=exc.response.status_code,
        content={"detail": exc.response.text or "External service error"},
    )