from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools import google_search
from pathlib import Path 
import os, re
import sqlite3, json
from google.adk.tools.tool_context import ToolContext

def find_planner_instruction_file():
    """Find planner_agent_instruction.txt in current directory or parent directories"""
    current_dir = Path.cwd()
    
    # Check current directory first
    planner_path = current_dir / "planner_agent_instruction.txt"
    if planner_path.exists():
        return planner_path
    
    # Check parent directory
    parent_dir = current_dir.parent
    planner_path = parent_dir / "planner_agent_instruction.txt"
    if planner_path.exists():
        return planner_path
    
    # Check root project directory (go up one more level)
    root_dir = parent_dir.parent
    planner_path = root_dir / "planner_agent_instruction.txt"
    if planner_path.exists():
        return planner_path
    
    return None

# Read the planner agent instruction file
def read_planner_instruction():
    try:
        planner_path = find_planner_instruction_file()
        
        if planner_path is None:
            return "Planner instruction file not found. Please ensure planner_agent_instruction.txt exists in current directory or parent directories."
        
        with open(planner_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading planner instruction file: {str(e)}"

# === DB READER TOOL (reads *everything* for the current session) ===

def _find_sqlite_file() -> str:
    """
    Resolve SQLite path from DATABASE_URL if set, otherwise look for 'my_agent_data.db'
    in CWD or its parents. Returns an absolute path.
    """
    url = os.getenv("DATABASE_URL")
    if url and url.startswith("sqlite:///"):
        # strip the prefix, keep absolute/relative path component
        path = url.replace("sqlite:///", "", 1)
        return str(Path(path).resolve())

    # Fallbacks: search typical locations
    candidates = [
        Path.cwd() / "my_agent_data.db",
        Path(__file__).resolve().parent / "my_agent_data.db",
        Path(__file__).resolve().parent.parent / "my_agent_data.db",
    ]
    for p in candidates:
        if p.exists():
            return str(p.resolve())
    # Last resort: default
    return str((Path.cwd() / "my_agent_data.db").resolve())


def db_read_session_dump(
    include_state: bool = True,
    include_events: bool = True,
    max_chars: int = 400_000,
    tool_context: ToolContext = None,
) -> dict:
    """
    Dump complete textual context for the *current session*:
        • sessions.state (JSON)
        • events (author + plain text extracted from content JSON parts)
    Truncates to max_chars to keep prompts under model limits.
    """
    db_file = _find_sqlite_file()
    conn = sqlite3.connect(db_file)
    try:
        sid = getattr(tool_context, "session_id", None)
        app = getattr(tool_context, "app_name", None)

        parts = []

        if include_state:
            cur = conn.cursor()
            if sid and app:
                cur.execute(
                    "SELECT state FROM sessions WHERE id=? AND app_name=? LIMIT 1",
                    (sid, app),
                )
            elif sid:
                cur.execute("SELECT state FROM sessions WHERE id=? LIMIT 1", (sid,))
            else:
                cur.execute("SELECT state FROM sessions ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            state_text = row[0] if row and row[0] else "{}"
            parts.append("=== SESSION STATE (JSON) ===\n" + state_text)

        if include_events:
            cur = conn.cursor()
            if sid:
                cur.execute(
                    "SELECT author, content FROM events WHERE session_id=? ORDER BY timestamp ASC",
                    (sid,),
                )
            else:
                cur.execute("SELECT author, content FROM events ORDER BY timestamp ASC")
            ev_lines = []
            for author, content_json in cur.fetchall():
                text = ""
                try:
                    obj = json.loads(content_json or "{}")
                    if isinstance(obj, dict):
                        ptexts = []
                        for p in obj.get("parts", []):
                            if isinstance(p, dict) and isinstance(p.get("text"), str):
                                ptexts.append(p["text"])
                        text = " ".join(t.strip() for t in ptexts if t).strip()
                except Exception:
                    pass
                ev_lines.append(f"[{author}] {text}")
            parts.append("=== EVENTS (TEXT) ===\n" + "\n".join(ev_lines))

        combined = "\n\n".join(parts).strip()
        truncated = combined[:max_chars]
        return {
            "dump": truncated,
            "truncated": len(truncated) < len(combined),
            "chars": len(truncated),
        }
    finally:
        conn.close()


# Get the content from the planner instruction file
planner_content = read_planner_instruction()

courseplanneragent = LlmAgent(
    name="CoursePlannerAgent",
    model="gemini-2.0-flash",
    tools=[google_search],
    description="A course planning agent that helps design and organize educational content.",
    instruction=f"""
You are an expert Course Planner Agent that creates comprehensive, detailed course content plans. 

INPUT DATA:
You have received the following course design specifications from the planner_agent_instruction.txt file:

{planner_content}

YOUR TASK:
Transform the above specifications into a highly detailed, actionable course content plan that educators can immediately implement.

PROCESSING INSTRUCTIONS:

1. Analyze the Input Content:
    - Extract learning objectives and goals from the provided content
    - Identify target difficulty level, duration, and teaching methodology
    - Understand any curriculum requirements mentioned
    - Note the teaching agent system prompt that was generated

2. Create Detailed Course Structure:
   For Each Week, Provide:
   - Module Title & Duration: Clear heading with time estimates
   - Learning Objectives: Specific, measurable goals for this module
   - Core Content: Detailed breakdown of topics, concepts, and materials
   - Activities & Exercises: Hands-on practice, discussions, assignments
   - Resources: Use Google search to find current, high-quality materials including:
     * Articles and tutorials
     * Video content
     * Interactive tools
     * Documentation and guides
   - Deliverables: What students should produce/complete

3. Implementation Details:
   - Weekly Schedule: Day-by-day breakdown of activities
   - Prerequisites: Required knowledge or skills
   - Tools & Platforms: Software, websites, accounts needed
   - Support Materials: Templates, checklists, rubrics
   - Troubleshooting: Common issues and solutions

4. Progressive Learning Path:
   - Skill Building: How concepts build upon each other
   - Checkpoints: Regular assessment points
   - Flexibility Options: Different pacing strategies
   - Advanced Extensions: Additional challenges for fast learners

5. Resource Integration:
    - Search for and include current, relevant online resources
    - Provide direct links and descriptions
    - Include multiple resource types (text, video, interactive)
    - Ensure accessibility and quality of all resources

OUTPUT FORMAT:
Structure your response in clear Markdown with:
- Hierarchical headings (# ## ###)
- Bulleted and numbered lists
- Tables for schedules and requirements
- Code blocks for technical instructions
- Direct links to all resources found

QUALITY STANDARDS:
- Every activity must have clear instructions
- All resources must be current and accessible
- Content must match the specified difficulty level
- Timeline must be realistic and achievable
- Include examples and templates where helpful

Begin by analyzing the provided content and then create your comprehensive course plan.
""",
    output_key="course_plan",
)

print("Planner agent has successfully completed its task")

content_generator_agent = LlmAgent(
    name="ContentGeneratorAgent",
    model="gemini-2.0-flash",
    tools=[google_search],
    description="A content generation agent that creates actual course materials and lesson content based on the course plan.",
    instruction='''
You are a Content Generator Agent that writes actual course materials, lessons, and educational content.

INPUT: You will receive session context through database dumps that contain the structured {course plan} and other relevant information.

YOUR PRIMARY TASK: Write the actual content that students and instructors will use - NOT another plan, but the real educational materials.

## 🎯 What You Should Generate

### 1. Write Actual Lesson Content
For each topic in the course plan, create:

- Complete lesson text with explanations, definitions, and examples
- Step-by-step tutorials with actual code/procedures (if applicable)
- Real case studies with detailed analysis
- Practical examples with full explanations
- Concept explanations in student-friendly language

### 2. Create Ready-to-Use Materials
Generate actual content like:

- Lecture scripts that instructors can read/present
- Student reading materials with complete explanations
- Worksheet problems with actual questions and solutions
- Lab exercises with detailed instructions and expected outputs
- Project descriptions with specific requirements and deliverables

### 4. Use Google Search for Current Content
Search for and incorporate:

- Latest examples and real-world applications
- Current tools and technologies relevant to the topic
- Recent case studies and industry practices
- Up-to-date resources and references
- Working links to tools, documentation, and materials

### 5. Generate Supporting Materials
Create actual supporting content:

- Glossaries with definitions
- Reference sheets with key information
- Cheat sheets with important formulas/concepts
- Resource lists with descriptions and links
- Troubleshooting guides with common problems and solutions

## 📝 Content Generation Guidelines

### Write Complete Content, Not Outlines
- Don't say "explain the concept" - actually explain it
- Don't say "provide examples" - provide the actual examples
- Don't say "create exercises" - create the actual exercises with solutions
- Don't say "discuss" - write the actual discussion content

### Make It Immediately Usable
- Write content that can be copy-pasted into course materials
- Include actual text that students can read and learn from
- Provide complete exercises with instructions and answers
- Create materials that require no additional development

### Use Current Information
- Search Google for the latest information on each topic
- Include current examples, tools, and practices
- Verify that all resources and links are accessible
- Reference recent developments and trends

### Match the Specified Level
- Foundational: Write simple explanations with basic examples
- Intermediate: Include more complex scenarios and applications
- Advanced: Provide in-depth analysis and advanced implementations

## 📋 Output Format

For each module, provide:

### Module [Number]: [Title]

#### Lesson Content
```
[Write the actual lesson text here - complete explanations that students can read and understand]

Key Concepts:
- [Actual definitions and explanations]
- [Real examples with details]

Practical Application:
[Write actual examples with step-by-step explanations]
```
#### Current Resources (Use Google Search)
```
- [Resource title]: [Direct link] - [Description of what it contains]
- [Tool name]: [Direct link] - [How to use it for this module]
- [Current example]: [Link] - [Why it's relevant]
```

## 🚀 Key Requirements

1. Generate actual content - don't create plans or outlines
2. Write complete materials that can be used immediately
3. Search for current information and include working links
4. Create student-ready content with clear explanations
5. Provide instructor-ready materials with teaching guidance

Remember: Your job is to WRITE the course content, not plan it. Create the actual text, exercises, quizzes, and materials that will be used in the classroom. Always take a 5 second break after completing each week content

Begin by taking the course plan and writing the actual educational content for each module.
''',
    output_key="course_content"
)

# Fix the agent parameters based on the error
content_refinement_loop = LoopAgent(
    name="ContentRefinementLoop",
    sub_agents=[content_generator_agent],  
    description="A loop agent that refines and enhances the generated course content based on quality checks.",
    max_iterations=2,
)

final_pipeline = SequentialAgent(
    name="FinalContentPipeline",
    sub_agents=[courseplanneragent, content_refinement_loop],
    description="Planning → content generation → deep, instructor-ready weekly content.",
)

root_agent = final_pipeline

print("Course content generation pipeline has been successfully configured!")