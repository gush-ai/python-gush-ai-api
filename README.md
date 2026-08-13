# File: README.md
# GitHub Release Manager

A production‑ready FastAPI service that wraps the **GitHub Releases API**. It provides type‑safe, synchronous (requests‑based) CRUD endpoints for managing releases across repositories in a single organization.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Docker Deployment](#docker-deployment)
- [API Reference](#api-reference)
- [Testing](#testing)
- [CI / CD](#ci--cd)
- [Security Considerations](#security-considerations)
- [License](#license)

## Features
- **List**, **Get**, **Create**, **Delete** GitHub releases.
- Strong typing with **Pydantic v2**.
- Synchronous GitHub client built on **requests** (simple, well‑tested).
- Centralized, dotenv‑based configuration.
- Health‑check endpoint (`/health`) for orchestration platforms.
- Fully containerized (Docker) and CI‑tested (GitHub Actions).

## Architecture
┌─────────────┐      ┌─────────────────────┐      ┌───────────────────────┐
│   Client    │◀────▶│   FastAPI (app/main)│◀────▶│   GitHub API (app/github)│
└─────────────┘      └─────────────────────┘      └───────────────────────┘
          ▲                ▲                     ▲
          │                │                     │
          │                │                     │
          │          Config (app/config.py)       │
          └───────────────────────────────────────┘
## Prerequisites
- Python 3.12+
- Docker (optional, for production)
- GitHub **Personal Access Token** with `repo` scope (or `public_repo` for public repos).

## Installation
## Configuration
Copy the example file and edit it:
Edit `.env`:
## Running Locally
Open <http://localhost:8000/docs> for the interactive OpenAPI UI.

## Docker Deployment
## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/orgs/{org}/repos/{repo}/releases` | List all releases for a repository. |
| `GET` | `/orgs/{org}/repos/{repo}/releases/{release_id}` | Retrieve a single release by ID. |
| `POST` | `/orgs/{org}/repos/{repo}/releases` | Create a new release. Payload matches `ReleaseCreatePayload`. |
| `DELETE` | `/orgs/{org}/repos/{repo}/releases/{release_id}` | Delete a release (204 No Content on success). |
| `GET` | `/health` | Health
# Run the full test suite
pytest -v
pytest --cov=app --cov-report=term-missing