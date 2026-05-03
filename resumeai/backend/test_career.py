import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from core.prompts import career_prompt
    from core.llm_client import llm_call

    fake_resume = """
ALAN SHINOJ
Python Developer | AI/ML Engineer

Experience:
- Built AI resume analyzer using FastAPI, LangChain, Python
- Developed NLP text processing pipeline with TensorFlow and Scikit-learn
- Created REST APIs with FastAPI and PostgreSQL backend
- Implemented deep learning models for sensor data processing
- Used Docker for containerization and deployment

Skills: Python, FastAPI, LangChain, TensorFlow, Scikit-learn, React, Docker, PostgreSQL, REST API, Git

Education: B.Tech Computer Science 2024

Projects:
- AI Resume Analyzer: Built full-stack resume analysis tool with NLP
- Real-time sensor data processing system with deep learning
"""
    prompt = career_prompt(fake_resume, "software engineer")
    print("Prompt length:", len(prompt))
    print("Calling LLM for career matching...")

    try:
        result = await llm_call(prompt, prompt_type="career_debug")
        print("SUCCESS - type:", type(result))
        print("Result:", str(result)[:1500])
    except Exception as e:
        print("ERROR:", type(e).__name__)
        print("Message:", str(e))

asyncio.run(test())