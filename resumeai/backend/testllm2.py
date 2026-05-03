import asyncio
import httpx
import sys
sys.path.insert(0, '.')

from core.config import settings

async def test():
    token = settings.hf_api_token
    print(f"Token loaded: {token[:8]}..." if token else "ERROR: No token found")

    # New HF Inference API URL format
    urls_to_try = [
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
        "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3/v1/chat/completions",
        "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
    ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        for url in urls_to_try:
            try:
                payload = {"inputs": "Reply with: {\"status\": \"working\"}", "parameters": {"max_new_tokens": 50, "return_full_text": False}}
                r = await client.post(url, json=payload, headers=headers, timeout=30)
                print(f"URL: {url}")
                print(f"Status: {r.status_code}")
                print(f"Response: {r.text[:300]}")
                print("---")
            except Exception as e:
                print(f"URL: {url} => ERROR: {e}")
                print("---")

asyncio.run(test())