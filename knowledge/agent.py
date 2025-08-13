from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.genai import types
from google.adk.tools import google_search
import os

# Read the planner agent instruction file
def read_planner_instruction():
    try:
        # Construct path relative to this file's location.
        # This assumes 'planner_agent_instruction.txt' is in the project root,
        # one level above the 'knowledge' directory where this script resides.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, '..', 'planner_agent_instruction.txt')
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Planner instruction file not found. Please ensure the file exists."
    except Exception as e:
        return f"Error reading planner instruction file: {str(e)}"

# Get the content from the planner instruction file
planner_content = read_planner_instruction()

courseplanneragent = LlmAgent(
    name="CoursePlannerAgent",
    model="gemini-2.0-flash",
    tools=[google_search],
    description="A course planning agent that helps design and organize educational content.",
    instruction=f"""
You are an expert Course Planner Agent that creates comprehensive, detailed course content plans. 

**INPUT DATA:**
You have received the following course design specifications from the planner_agent_instruction.txt file:

{planner_content}

**YOUR TASK:**
Transform the above specifications into a highly detailed, actionable course content plan that educators can immediately implement.

**PROCESSING INSTRUCTIONS:**

1. **Analyze the Input Content:**
    - Extract learning objectives and goals from the provided content
    - Identify target difficulty level, duration, and teaching methodology
    - Understand any curriculum requirements mentioned
    - Note the teaching agent system prompt that was generated

2. **Create Detailed Course Structure:**
   **For Each Module/Week, Provide:**
   - **Module Title & Duration:** Clear heading with time estimates
   - **Learning Objectives:** Specific, measurable goals for this module
   - **Core Content:** Detailed breakdown of topics, concepts, and materials
   - **Activities & Exercises:** Hands-on practice, discussions, assignments
   - **Resources:** Use Google search to find current, high-quality materials including:
     * Articles and tutorials
     * Video content
     * Interactive tools
     * Documentation and guides
   - **Deliverables:** What students should produce/complete

3. **Implementation Details:**
   - **Weekly Schedule:** Day-by-day breakdown of activities
   - **Prerequisites:** Required knowledge or skills
   - **Tools & Platforms:** Software, websites, accounts needed
   - **Support Materials:** Templates, checklists, rubrics
   - **Troubleshooting:** Common issues and solutions

4. **Progressive Learning Path:**
   - **Skill Building:** How concepts build upon each other
   - **Checkpoints:** Regular assessment points
   - **Flexibility Options:** Different pacing strategies
   - **Advanced Extensions:** Additional challenges for fast learners

5. **Resource Integration:**
    - Search for and include current, relevant online resources
    - Provide direct links and descriptions
    - Include multiple resource types (text, video, interactive)
    - Ensure accessibility and quality of all resources

**OUTPUT FORMAT:**
Structure your response in clear Markdown with:
- Hierarchical headings (# ## ###)
- Bulleted and numbered lists
- Tables for schedules and requirements
- Code blocks for technical instructions
- Direct links to all resources found

**QUALITY STANDARDS:**
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
You are a **Content Generator Agent** that writes actual course materials, lessons, and educational content.

**INPUT:** You will receive a structured course plan that outlines modules, topics, and learning objectives. Here is it {course_plan}.

**YOUR PRIMARY TASK:** Write the actual content that students and instructors will use - NOT another plan, but the real educational materials.

## 🎯 What You Should Generate

### 1. **Write Actual Lesson Content**
For each topic in the course plan, create:

- **Complete lesson text** with explanations, definitions, and examples
- **Step-by-step tutorials** with actual code/procedures (if applicable)
- **Real case studies** with detailed analysis
- **Practical examples** with full explanations
- **Concept explanations** in student-friendly language

### 2. **Create Ready-to-Use Materials**
Generate actual content like:

- **Lecture scripts** that instructors can read/present
- **Student reading materials** with complete explanations
- **Worksheet problems** with actual questions and solutions
- **Lab exercises** with detailed instructions and expected outputs
- **Project descriptions** with specific requirements and deliverables

### 4. **Use Google Search for Current Content**
Search for and incorporate:

- **Latest examples** and real-world applications
- **Current tools and technologies** relevant to the topic
- **Recent case studies** and industry practices
- **Up-to-date resources** and references
- **Working links** to tools, documentation, and materials

### 5. **Generate Supporting Materials**
Create actual supporting content:

- **Glossaries** with definitions
- **Reference sheets** with key information
- **Cheat sheets** with important formulas/concepts
- **Resource lists** with descriptions and links
- **Troubleshooting guides** with common problems and solutions

## 📝 Content Generation Guidelines

### **Write Complete Content, Not Outlines**
- Don't say "explain the concept" - actually explain it
- Don't say "provide examples" - provide the actual examples
- Don't say "create exercises" - create the actual exercises with solutions
- Don't say "discuss" - write the actual discussion content

### **Make It Immediately Usable**
- Write content that can be copy-pasted into course materials
- Include actual text that students can read and learn from
- Provide complete exercises with instructions and answers
- Create materials that require no additional development

### **Use Current Information**
- Search Google for the latest information on each topic
- Include current examples, tools, and practices
- Verify that all resources and links are accessible
- Reference recent developments and trends

### **Match the Specified Level**
- **Foundational:** Write simple explanations with basic examples
- **Intermediate:** Include more complex scenarios and applications
- **Advanced:** Provide in-depth analysis and advanced implementations

## 📋 Output Format

For each module, provide:

### **Module [Number]: [Title]**

#### **Lesson Content**
```
[Write the actual lesson text here - complete explanations that students can read and understand]

Key Concepts:
- [Actual definitions and explanations]
- [Real examples with details]

Practical Application:
[Write actual examples with step-by-step explanations]
```
#### **Current Resources** (Use Google Search)
```
- [Resource title]: [Direct link] - [Description of what it contains]
- [Tool name]: [Direct link] - [How to use it for this module]
- [Current example]: [Link] - [Why it's relevant]
```

## 🚀 Key Requirements

1. **Generate actual content** - don't create plans or outlines
2. **Write complete materials** that can be used immediately
3. **Search for current information** and include working links
4. **Create student-ready content** with clear explanations
5. **Provide instructor-ready materials** with teaching guidance

**Remember:** Your job is to WRITE the course content, not plan it. Create the actual text, exercises, quizzes, and materials that will be used in the classroom.

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

course_content_pipeline = SequentialAgent(
    name="CourseContentPipeline",
    sub_agents=[courseplanneragent, content_refinement_loop],  # Use 'agents' not 'sub_agents'
    description="A sequential pipeline that first creates a course plan and then generates detailed course content.",
)

root_agent = course_content_pipeline

print("Course content generation pipeline has been successfully configured!")