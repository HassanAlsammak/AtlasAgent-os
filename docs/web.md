# AtlasAgent OS Web UI — local-first prototype

## Requirements
Python 3.10+, FastAPI, Uvicorn, HTTPX (for tests). The web app serves its own static HTML/CSS/JS; no Node build or cloud account is needed.

## Windows quickstart
```powershell
git clone https://github.com/HassanAlsammak/AtlasAgent-os.git
cd AtlasAgent-os
py -m venv .venv
.venv\Scripts\python -m pip install -e ".[web]"
.venv\Scripts\python -m uvicorn atlasagent.web:app --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000 and visit http://127.0.0.1:8000/api/docs for API documentation.

## Optional AI mode
Set `ATLASAGENT_API_KEY` in the server environment before starting. Choose AI mode and provide the exact provider model ID. The current adapter calls the OpenAI-compatible HTTPS chat-completions endpoint, sends your prompt to the provider, and may incur costs. Offline mode is free and deterministic.

## Safety
**Do not expose this development server to the public internet.** The default bind address is loopback. Set `ATLAS_WEB_TOKEN` to require an `X-Atlas-Token` header for API calls (the bundled browser UI does not yet support that header). Browser UI is designed for single-user local operation only. Rate limiting is in-memory and per-process, and the app has no authentication sessions, CSRF protection, persistence, or production hardening.

No real computer control or code execution is exposed through this web UI. The UI uses textContent to render model output, not HTML injection.

## Tests
```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```
