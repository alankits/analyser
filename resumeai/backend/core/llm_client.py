from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

# New HuggingFace Inference Providers router endpoint (replaces old api-inference.huggingface.co)
_HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"

# Models that work on the free tier via Inference Providers
_PRIMARY_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
_FALLBACK_MODEL = "Qwen/Qwen2.5-7B-Instruct"

_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 2.0
_REQUEST_TIMEOUT_SECONDS = 120.0


def _build_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.hf_api_token}",
        "Content-Type": "application/json",
    }


def _extract_json(raw: str) -> Any:
    """Parse JSON from LLM output, stripping any markdown fences or preamble."""
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    raw = raw.replace("```", "").strip()

    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = raw.find(start_char)
        if start != -1:
            depth = 0
            for i, ch in enumerate(raw[start:], start=start):
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        candidate = raw[start: i + 1]
                        return json.loads(candidate)

    raise ValueError(f"No valid JSON found in LLM output: {raw[:300]!r}")


async def _call_model(
    client: httpx.AsyncClient,
    model: str,
    prompt: str,
) -> Any:
    """Send a single chat completion request and return parsed JSON."""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a precise AI assistant. "
                    "You always respond with valid JSON only. "
                    "Never include explanations, markdown, or any text outside the JSON object."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
        "stream": False,
    }

    response = await client.post(
        _HF_ROUTER_URL,
        json=payload,
        headers=_build_headers(),
        timeout=_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    result = response.json()

    # OpenAI-compatible response format
    generated = result["choices"][0]["message"]["content"]
    return _extract_json(generated)


async def llm_call(prompt: str, prompt_type: str = "generic") -> Any:
    """
    Call LLM via HuggingFace Inference Providers with retry and fallback.
    Returns parsed JSON.
    """
    from utils.cache import cache_get, cache_set

    cache_key = hashlib.sha256(f"{prompt_type}:{prompt}".encode()).hexdigest()

    cached = await cache_get(cache_key)
    if cached is not None:
        logger.info("Cache hit for prompt_type=%s", prompt_type)
        return cached

    # Use config models if set, otherwise use free-tier defaults
    primary = getattr(settings, "hf_primary_model", _PRIMARY_MODEL) or _PRIMARY_MODEL
    fallback = getattr(settings, "hf_fallback_model", _FALLBACK_MODEL) or _FALLBACK_MODEL
    models_to_try = [primary, fallback]

    async with httpx.AsyncClient() as client:
        for model_index, model in enumerate(models_to_try):
            for attempt in range(1, _MAX_RETRIES + 1):
                try:
                    logger.info(
                        "LLM call: model=%s attempt=%d prompt_type=%s",
                        model, attempt, prompt_type,
                    )
                    result = await _call_model(client, model, prompt)
                    await cache_set(cache_key, result)
                    return result

                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    body = exc.response.text[:300]
                    logger.warning(
                        "HTTP %d from model=%s attempt=%d body=%s",
                        status, model, attempt, body,
                    )
                    if status == 401:
                        raise RuntimeError(
                            "HuggingFace token is invalid or missing "
                            "'Make calls to Inference Providers' permission. "
                            "Go to huggingface.co → Settings → Access Tokens and enable it."
                        ) from exc
                    if status in (429, 503) and attempt < _MAX_RETRIES:
                        await asyncio.sleep(_RETRY_DELAY_SECONDS * attempt)
                        continue
                    if status < 500 and status != 429:
                        break

                except (json.JSONDecodeError, ValueError) as exc:
                    logger.warning(
                        "JSON parse error model=%s attempt=%d: %s",
                        model, attempt, str(exc),
                    )
                    if attempt < _MAX_RETRIES:
                        await asyncio.sleep(_RETRY_DELAY_SECONDS)
                        continue
                    break

                except httpx.RequestError as exc:
                    logger.warning(
                        "Request error model=%s attempt=%d: %s",
                        model, attempt, str(exc),
                    )
                    if attempt < _MAX_RETRIES:
                        await asyncio.sleep(_RETRY_DELAY_SECONDS * attempt)
                        continue
                    break

            if model_index < len(models_to_try) - 1:
                logger.warning(
                    "Model %s exhausted retries, switching to fallback %s",
                    model, models_to_try[model_index + 1],
                )

    raise RuntimeError(
        "All LLM models failed. Check your HuggingFace token has "
        "'Make calls to Inference Providers' permission enabled."
    )