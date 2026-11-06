"""Local-first AtlasAgent OS web API.

Run: python -m uvicorn atlasagent.web:app --host 127.0.0.1 --port 8000
Do not expose this development server to the public internet.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import os
import secrets
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from .core import Runner, Task, template_agent
from .guardian import review_unified_diff
from .providers import chat_completion, ProviderError

app = FastAPI(title="AtlasAgent OS", version="0.3.0", docs_url="/api/docs", redoc_url=None)
STATIC = Path(__file__).resolve().parent / "static"
# Optional shared token for local API use. Required for remote deployments.
API_TOKEN = os.getenv("ATLAS_WEB_TOKEN")
MAX_REQUESTS = 30
WINDOW_SECONDS = 60
_hits: dict[str, list[float]] = {}

class RunRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=4000)
    mode: str = Field(default="offline", pattern="^(offline|llm)$")
    model: str = Field(default="", max_length=128)

class ReviewRequest(BaseModel):
    diff: str = Field(min_length=1, max_length=200000)

@app.middleware("http")
async def local_security(request: Request, call_next):
    # Default bind is loopback. Require token when explicitly configured.
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        if API_TOKEN and not secrets.compare_digest(request.headers.get("x-atlas-token", ""), API_TOKEN):
            return JSONResponse({"detail": "Invalid API token"}, status_code=401)
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        recent = [t for t in _hits.get(client, []) if now - t < WINDOW_SECONDS]
        if len(recent) >= MAX_REQUESTS:
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        recent.append(now)
        _hits[client] = recent
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", media_type="text/html")

@app.get("/static/app.js")
def script():
    return FileResponse(STATIC / "app.js", media_type="application/javascript")

@app.get("/static/style.css")
def style():
    return FileResponse(STATIC / "style.css", media_type="text/css")

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.3.0", "mode": "local-first"}

@app.post("/api/run")
def run(request: RunRequest):
    if request.mode == "llm":
        if not request.model:
            raise HTTPException(status_code=422, detail="Model is required for LLM mode")
        if not os.getenv("ATLASAGENT_API_KEY"):
            raise HTTPException(status_code=400, detail="Configure ATLASAGENT_API_KEY on the server")
        try:
            response = chat_completion(request.goal, model=request.model)
        except ProviderError:
            raise HTTPException(status_code=502, detail="AI provider request failed")
        return {"mode": "llm", "steps": [{"role": "assistant", "output": response}]}
    runner = Runner({role: template_agent(role) for role in ("planner", "builder", "reviewer")})
    results = runner.execute([
        Task("plan", "planner", request.goal),
        Task("build", "builder", "Create an implementation outline", ("plan",)),
        Task("review", "reviewer", "Review the outline", ("build",)),
    ])
    return {"mode": "offline", "steps": [asdict(item) for item in results], "audit": runner.audit}

@app.post("/api/guardian")
def guardian(request: ReviewRequest):
    findings = review_unified_diff(request.diff)
    return {"findings": [asdict(item) for item in findings], "count": len(findings)}
