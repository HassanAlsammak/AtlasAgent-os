"""Optional OpenAI-compatible chat-completions adapter (standard library only)."""
from __future__ import annotations
import json
import os
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

class ProviderError(RuntimeError):
    pass

def chat_completion(prompt: str, *, model: str, api_key: str | None = None,
                    base_url: str = "https://api.openai.com/v1", timeout: float = 30.0,
                    max_tokens: int = 512) -> str:
    """Call a trusted HTTPS provider. No automatic retries or tool execution."""
    if not 0 < len(prompt) <= 30_000:
        raise ValueError("Prompt must be 1-30000 characters")
    if not model or len(model) > 128:
        raise ValueError("Invalid model name")
    if not 0 < timeout <= 120 or not 1 <= max_tokens <= 4096:
        raise ValueError("Invalid request limits")
    url = base_url.rstrip("/") + "/chat/completions"
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Provider URL must be a valid HTTPS URL")
    key = api_key or os.environ.get("ATLASAGENT_API_KEY")
    if not key:
        raise ProviderError("Set ATLASAGENT_API_KEY or pass api_key")
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                          "max_tokens": max_tokens}).encode()
    request = Request(url, data=payload, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "User-Agent": "AtlasAgent-OS/0.2"}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ProviderError("Provider response too large")
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ProviderError("Provider returned non-text content")
        return content
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ProviderError("Unexpected provider response format") from exc
