# deep_runner.py
import asyncio
import os, sys
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

# If your llm.py lives one level up (same pattern as your main.py does)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm import user_name, user_id

# ✅ Import ONLY the deep content pipeline (your deep content agent/loop)
# Assumes you placed the deep agent in knowledge_1/agent.py with root_agent or deep loop exported.
try:
    from knowledge_1.agent import root_agent as deep_pipeline
except ModuleNotFoundError:
    # fallback if your deep agent module is named differently
    from knowledge_1.agent import deep_content_loop as deep_pipeline  # adjust if needed

load_dotenv()

APP_NAME = "AI Copilot for Instructors"

async def main_async():
    # Use the SAME SQLite DB as the first run
    db_url = os.getenv("DATABASE_URL") or "sqlite:///./my_agent_data.db"
    os.environ["DATABASE_URL"] = db_url  # so the db_read_session_dump tool resolves the same file
    session_service = DatabaseSessionService(db_url=db_url)

    # Reuse the same session created by the first pipeline
    existing = await session_service.list_sessions(app_name=APP_NAME, user_id=user_id)
    if existing and existing.sessions:
        SESSION_ID = existing.sessions[0].id
        print(f"Using existing session: {SESSION_ID}")
    else:
        # If no session exists yet (e.g., you run this first by mistake), create one seeded the same way.
        initial_state = {"user_name": user_name, "user_id": user_id}
        new_sess = await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, state=initial_state
        )
        SESSION_ID = new_sess.id
        print(f"Created new session (no prior content found): {SESSION_ID}")

    runner = Runner(agent=deep_pipeline, app_name=APP_NAME, session_service=session_service)

    # Kick off the deep generation; the agent will read the ENTIRE DB via its tool before writing.
    prompt = "Continue deep content generation. Read the whole DB (state + events) and produce the next full week."
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=user_id, session_id=SESSION_ID, new_message=content
    ):
        if event.is_final_response():
            print("Deep generation finished.")

    # Inspect what got saved
    sess = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=SESSION_ID)
    print("Saved keys in state:", list(sess.state.keys()))
    deep = sess.state.get("deep_course_content")
    if deep:
        print("\n=== deep_course_content (preview) ===\n", deep[:1200], "...\n")
    else:
        print("No deep_course_content yet. Check logs or increase tool max_chars.")
    
if __name__ == "__main__":
    asyncio.run(main_async())
