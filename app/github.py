# File: app/github.py
import requests
from typing import List, Dict, Any, Optional
from .config import settings
import logging

_logger = logging.getLogger(__name__)

def _headers() -> Dict[str, str]:
    """Create the Authorization and Accept headers for GitHub API calls."""
    return {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "gush-release-manager/1.0"
    }

def _handle_response(resp: requests.Response) -> Any:
    """Raise for HTTP errors and return JSON payload."""
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        _logger.error(
            "GitHub API error %s %s: %s",
            resp.status_code,
            resp.url,
            resp.text
        )
        raise exc
    if resp.content:
        return resp.json()
    return None

def list_releases(repo: str) -> List[Dict[str, Any]]:
    """Return a list of releases for a given repository."""
    url = f"{settings.GITHUB_API_URL}/repos/{settings.GITHUB_ORG}/{repo}/releases"
    resp = requests.get(url, headers=_headers())
    return _handle_response(resp)

def get_release(repo: str, release_id: int) -> Dict[str, Any]:
    """Retrieve a single release by its numeric ID."""
    url = f"{settings.GITHUB_API_URL}/repos/{settings.GITHUB_ORG}/{repo}/releases/{release_id}"
    resp = requests.get(url, headers=_headers())
    return _handle_response(resp)

def create_release(
    repo: str,
    tag_name: str,
    name: Optional[str] = None,
    body: Optional[str] = None,
    draft: bool = False,
    prerelease: bool = False,
    target_commitish: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new release."""
    payload: Dict[str, Any] = {
        "tag_name": tag_name,
        "draft": draft,
        "prerelease": prerelease,
    }
    if name is not None:
        payload["name"] = name
    if body is not None:
        payload["body"] = body
    if target_commitish is not None:
        payload["target_commitish"] = target_commitish

    url = f"{settings.GITHUB_API_URL}/repos/{settings.GITHUB_ORG}/{repo}/releases"
    resp = requests.post(url, headers=_headers(), json=payload)
    return _handle_response(resp)

def delete_release(repo: str, release_id: int) -> None:
    """Delete a release by its numeric ID."""
    url = f"{settings.GITHUB_API_URL}/repos/{settings.GITHUB_ORG}/{repo}/releases/{release_id}"
    resp = requests.delete(url, headers=_headers())
    _handle_response(resp)  # Will raise on error; returns None on success