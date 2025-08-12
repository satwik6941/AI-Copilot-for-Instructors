# main.py
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

# if you're running from the parent folder and importing llm:
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm import user_name, user_id

from knowledge.agent import final_pipeline  # your pipeline (SequentialAgent)

load_dotenv()

db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

initial_state = {
    "user_name": user_name,
    "user_id": user_id,
}

async def main_async():
    APP_NAME = "AI Copilot for Instructors"
    USER_ID = user_id

    # ✅ await these calls
    existing = await session_service.list_sessions(app_name=APP_NAME, user_id=USER_ID)
    if existing and len(existing.sessions) > 0:
        SESSION_ID = existing.sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
    else:
        new_sess = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, state=initial_state
        )
        SESSION_ID = new_sess.id
        print(f"Created new session: {SESSION_ID}")

    runner = Runner(agent=final_pipeline, app_name=APP_NAME, session_service=session_service)

    # Kick off the pipeline with any simple user message
    content = types.Content(role="user", parts=[types.Part(text="Please generate the full course now.")])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
        if event.is_final_response():
            print("Generation finished.")

    # ✅ Verify outputs were saved to SQLite session.state via output_key
    sess = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    print("Saved keys in state:", list(sess.state.keys()))
    # Example: print a short preview
    deep = sess.state.get("deep_course_content")
    if deep:
        print("deep_course_content (preview):", deep[:400], "...")
    else:
        print("No deep_course_content yet.")

if __name__ == "__main__":
    asyncio.run(main_async())
