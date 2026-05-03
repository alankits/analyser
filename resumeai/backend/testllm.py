import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    try:
        from core.llm_client import llm_call
        prompt = "<s>[INST] Reply with this exact JSON and nothing else: {\"status\": \"working\"} [/INST]"
        result = await llm_call(prompt, prompt_type="test")
        print("SUCCESS:", result)
    except Exception as e:
        print("ERROR:", type(e).__name__, str(e))

asyncio.run(test())