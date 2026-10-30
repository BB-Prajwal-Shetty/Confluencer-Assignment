"""Thin provider-agnostic LLM client. Set LLM_PROVIDER to gemini | anthropic | openai."""
import os

import httpx

TIMEOUT = httpx.Timeout(60.0)


class LLMError(Exception):
    pass


async def complete(system: str, prompt: str, temperature: float = 0.8) -> str:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider == "gemini":
        return await _gemini(system, prompt, temperature)
    if provider == "anthropic":
        return await _anthropic(system, prompt, temperature)
    if provider == "openai":
        return await _openai(system, prompt, temperature)
    raise LLMError(f"Unknown LLM_PROVIDER '{provider}'. Use gemini, anthropic or openai.")


def _key(name: str) -> str:
    key = os.getenv(name)
    if not key:
        raise LLMError(f"{name} is not set. Add it to your .env file or hosting environment variables.")
    return key


async def _post(client: httpx.AsyncClient, url: str, **kwargs) -> dict:
    try:
        resp = await client.post(url, **kwargs)
    except httpx.HTTPError as e:
        raise LLMError(f"Could not reach the LLM API: {e.__class__.__name__}")
    if resp.status_code >= 400:
        raise LLMError(f"LLM API error {resp.status_code}: {resp.text[:300]}")
    return resp.json()


async def _gemini(system, prompt, temperature):
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"},
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        data = await _post(client, url, json=body, headers={"x-goog-api-key": _key("GEMINI_API_KEY")})
    try:
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        raise LLMError("Gemini returned no content (the request may have been blocked).")


async def _anthropic(system, prompt, temperature):
    body = {
        "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        "max_tokens": 2000,
        "temperature": temperature,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"x-api-key": _key("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        data = await _post(client, "https://api.anthropic.com/v1/messages", json=body, headers=headers)
    return "".join(b.get("text", "") for b in data.get("content", []))


async def _openai(system, prompt, temperature):
    body = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    }
    headers = {"Authorization": f"Bearer {_key('OPENAI_API_KEY')}"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        data = await _post(client, "https://api.openai.com/v1/chat/completions", json=body, headers=headers)
    return data["choices"][0]["message"]["content"]
