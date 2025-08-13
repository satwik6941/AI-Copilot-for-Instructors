# llm.py — v1 web-friendly generate function (no CLI, no local paths)
# Purpose: Single-pass generation of a structured module draft (lesson plan + exercises + quiz)
# Model: gemini-2.0-flash
# Inputs: title, level, duration_weeks, teaching_style, optional curriculum PDF bytes
# Output: Python dict matching the strict schema (ready for UI + PDF export)

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from typing import Optional, Dict, Any

load_dotenv()

# ---- Strict schema contract for UI/PDF ----
# Returned JSON MUST match this shape:
# {
#   "meta": { "title": str, "level": "Beginner|Intermediate|Advanced", "durationWeeks": int, "teachingStyle": str },
#   "objectives": [str, ...],
#   "lessons": [ { "id": str, "title": str, "summary": str, "content": str, "resources": [str, ...]? }, ...],
#   "exercises": [ { "id": str, "prompt": str, "expectedOutcome": str }, ...],
#   "quiz": [ { "id": str, "question": str, "choices": [str, ...], "answer": str, "explanation": str }, ...]
# }

SYSTEM_INSTRUCTION = """
You generate strictly structured course **module drafts** for instructors.

Return **ONLY** valid JSON (no prose) matching the provided schema exactly.
Do not include keys not present in the schema. Use concise, clear language.

Rules:
- Reflect `level` (Beginner/Intermediate/Advanced) in depth and tone.
- Follow `teachingStyle` (e.g., "Explain → Example → Exercise") in how lessons are written.
- If a curriculum PDF is provided, align topics/sequence to it (summarize/adapt; do not copy tables verbatim).
- Produce 3–6 clear objectives.
- Create 4–10 lessons total (depending on duration), each with: title, 1–2 sentence summary, and student-facing content (markdown acceptable).
- Include practical exercises (3–6 items) with expected outcomes.
- Include a quiz with 5–8 items; each has choices, correct answer, and explanation.
- No external web browsing for generation.
"""

def _normalize_level(level: str) -> str:
    if not level:
        return "Beginner"
    l = level.strip().lower()
    if l.startswith("beg"): return "Beginner"
    if l.startswith("int"): return "Intermediate"
    if l.startswith("adv"): return "Advanced"
    return "Beginner"

def _safe_json_parse(text: str) -> Dict[str, Any]:
    # Some LLMs may wrap JSON with code fences; strip them defensively.
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        # remove potential leading language identifier after backticks
        first_brace = t.find("{")
        t = t[first_brace:] if first_brace != -1 else t
    return json.loads(t)

def generate_module(
    title: str,
    level: str,
    duration_weeks: int,
    teaching_style: str,
    curriculum_pdf_bytes: Optional[bytes] = None,
    curriculum_pdf_mime: str = "application/pdf",
) -> Dict[str, Any]:
    """
    Web-friendly entry point:
    - Call this from your API route/controller.
    - Provide curriculum_pdf_bytes if an instructor uploaded a PDF (optional in v1).
    - Returns a Python dict ready for your UI.
    """
    if not title or not isinstance(title, str):
        raise ValueError("title is required (non-empty string)")
    if not isinstance(duration_weeks, int) or duration_weeks <= 0:
        raise ValueError("duration_weeks must be a positive integer")
    level_norm = _normalize_level(level)
    teaching_style = teaching_style or "Explain → Example → Exercise"

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    contents = [
        types.Part.from_text(json.dumps({
            "meta": {
                "title": title,
                "level": level_norm,
                "durationWeeks": duration_weeks,
                "teachingStyle": teaching_style
            }
        }))
    ]

    if curriculum_pdf_bytes:
        contents.append(
            types.Part.from_bytes(
                data=curriculum_pdf_bytes,
                mime_type=curriculum_pdf_mime
            )
        )

    # Ask the model to produce ONLY valid JSON per our contract.
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            # No tools for v1 generation (freshness uses curated feeds in a separate step).
            temperature=0.4,
            top_p=0.9,
        ),
    )

    # Convert response to JSON dict safely
    text = getattr(resp, "text", None) or ""
    try:
        data = _safe_json_parse(text)
    except Exception as e:
        raise RuntimeError(f"Model did not return valid JSON: {e}\nRaw: {text[:500]}")

    # Minimal validation (keep it lightweight)
    required_top = ["meta", "objectives", "lessons", "exercises", "quiz"]
    for k in required_top:
        if k not in data:
            raise RuntimeError(f"Generated JSON missing required key: {k}")

    return data
