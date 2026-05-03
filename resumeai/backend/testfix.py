import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from core.prompts import fix_prompt
    from core.llm_client import llm_call

    # Simple fake resume to test with
    fake_resume = """
John Doe
Software Engineer

Experience:
- Worked on websites
- Helped customers with issues
- Responsible for coding the backend
- Assisted with database management

Skills: Python, JavaScript, React

Education: BSc Computer Science, 2022
"""
    prompt = fix_prompt(fake_resume)
    print("Prompt length:", len(prompt))
    print("Calling LLM...")

    try:
        result = await llm_call(prompt, prompt_type="fix_test")
        print("SUCCESS - type:", type(result))
        print("Result:", str(result)[:1000])
    except Exception as e:
        print("ERROR:", type(e).__name__)
        print("Message:", str(e))

asyncio.run(test())