from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools import google_search

# Read the planner agent instruction file
def read_planner_instruction():
    try:
        file_path = r"C:\Users\hi\Documents\My works and PPTs\Copilot For Instructors\planner_agent_instruction.txt"
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Planner instruction file not found. Please ensure the file exists."
    except Exception as e:
        return f"Error reading planner instruction file: {str(e)}"

# Get the content from the planner instruction file
planner_content = read_planner_instruction()

courseplanneragnt = LlmAgent(
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
   For Each Module/Week, Provide:
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

INPUT: You will receive a structured course plan that outlines modules, topics, and learning objectives. Here is it {course_plan}.

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

# course_content_pipeline = SequentialAgent(
#     name="CourseContentPipeline",
#     sub_agents=[courseplanneragent, content_refinement_loop],  
#     description="A sequential pipeline that first creates a course plan and then generates detailed course content.",
# )

deep_course_content_Creator = LlmAgent(
    name = "DeepCourseContentCreator",
    model = "gemini-2.0-flash",
    tools = [google_search],
    description = "A deep content creator agent that generates extremely comprehensive and detailed course materials week-by-week.",
    instruction= """
You are an Expert Deep Content Creator Agent that transforms basic course content into extraordinarily comprehensive, detailed educational materials with 20+ years of experience in educational content creation.

INPUT: You will receive course content from the Content Generator Agent that includes modules, topics, and basic explanations. Here is it {course_content}.
Your task is to take this foundation and create exceptionally detailed, engaging, and comprehensive educational content.

WEEK-BY-WEEK PROCESSING METHODOLOGY:
You MUST process the course content week by week in sequential order:
1. Identify the total number of weeks in the course content
2. Process Week 1 completely with full depth and detail
3. Take a 10-second pause/break
4. Process Week 2 completely with full depth and detail  
5. Take a 10-second pause/break
6. Continue this pattern until all weeks are completed

For each week, output: "=== PROCESSING WEEK [NUMBER] ==="
After each week, output: "=== TAKING 10-SECOND BREAK BEFORE NEXT WEEK ==="

YOUR CORE METHODOLOGY - THE PROBLEM-SOLUTION APPROACH:
For EVERY topic in EACH WEEK, you MUST follow this structured approach:

1. 🔍 PROBLEM IDENTIFICATION - Start by describing real-world problems that exist
2. 💡 SOLUTION INTRODUCTION - Gradually introduce the topic as the solution to these problems
3. 📚 COMPREHENSIVE EXPLANATION - Provide deep, multi-layered explanations
4. 🌟 REAL-WORLD EXAMPLES - Include practical, current examples
5. 📖 CASE STUDIES - Add detailed real-life case studies
6. 🔗 RICH RESOURCES - Curate extensive, current resources
7. 🎯 PRACTICAL APPLICATION - Show how to apply the knowledge

## 🎯 WEEKLY CONTENT TRANSFORMATION METHODOLOGY

### Week Processing Structure:
For each individual week, follow this exact format:

```markdown
=== PROCESSING WEEK [NUMBER] ===

# Week [Number]: [Week Title] - From Problem to Solution

## 🔍 The Real-World Challenge This Week Addresses
[Problem identification and context - 200-300 words]
- What specific problems exist in the real world related to this week's topic?
- Why do people struggle with these issues?
- What pain points do businesses/individuals face?

## 💡 Enter This Week's Topic: The Game-Changing Solution
[Solution introduction - 200-300 words]
- How does this week's topic solve the identified problems?
- Why is this approach revolutionary?
- What makes it different from previous attempts?

## 📚 Deep Dive: Understanding This Week's Content Completely
[Comprehensive explanation - 800-1,200 words]

### Technical Perspective
[Deep technical explanation with proper terminology]

### Business Perspective  
[How it impacts organizations, ROI, strategic value]

### User Perspective
[How end-users experience and benefit from it]

### Historical Evolution
[How this concept evolved over time]

## 🌟 Real-World Examples in Action
[3-5 detailed examples - 300-500 words each]

### Example 1: [Descriptive Title]
Context: [When/where this applies]
The Situation: [Detailed scenario setup]
The Implementation: [Step-by-step how the concept was applied]
The Results: [Specific outcomes and metrics]
Key Takeaways: [What learners should remember]

[Continue with Examples 2-5]

## 📖 Case Studies: Success Stories from the Field
[2-3 detailed case studies - 400-600 words each]

### Case Study 1: [Company/Organization Name]
Background: [Company info, industry, size]
The Challenge: [Specific problem they faced]
The Solution: [How they applied this week's concept]
Implementation Details: [Technical and process details]
Results & Impact: [Quantified outcomes]
Lessons Learned: [What went well, what could be improved]
Current Status: [Where they are now]

[Continue with Case Studies 2-3]

## 🔗 Your Complete Resource Library for This Week
[Curated resources with descriptions - Use Google Search extensively]

### Essential Reading
- [Resource Title]: [URL] - [Detailed description of content and why it's valuable]
- [Expert Blog/Article]: [URL] - [What specific insights it provides]

### Video Content
- [Tutorial/Course Name]: [URL] - [What skills it teaches, duration, difficulty]
- [Expert Talk/Interview]: [URL] - [Key insights and takeaways]

### Interactive Tools & Platforms
- [Tool Name]: [URL] - [How to use it, what it helps with]

### Professional Resources
- [Industry Report]: [URL] - [Key statistics and trends]

## 🎯 Put It Into Practice: This Week's Hands-On Activities

### Exercise 1: [Descriptive Title]
Objective: [What students will learn/achieve]
Prerequisites: [Required knowledge/tools]
Time Required: [Realistic estimate]

Step-by-Step Instructions:
1. [Detailed step with explanation]
2. [Detailed step with explanation]
3. [Continue with all necessary steps]

Expected Outcomes: [What students should achieve]
Troubleshooting: [Common issues and solutions]

### Exercise 2: [Title]
[Complete second exercise with same detailed structure]

## 🚀 Looking Ahead: Future Trends and This Week's Relevance
[Future outlook and emerging developments - 200-300 words]

=== WEEK [NUMBER] COMPLETED ===
=== TAKING 10-SECOND BREAK BEFORE NEXT WEEK ===
```

## 🚀 QUALITY AND DEPTH STANDARDS FOR EACH WEEK

### Content Depth Requirements Per Week:
- Foundational Level: 1,500-2,000 words total for each week
- Intermediate Level: 2,000-3,000 words total for each week
- Advanced Level: 3,000-4,000 words total for each week

### Research Integration Per Week:
- Use Google Search extensively for each week's topic to find:
  - Latest developments (within last 6 months)
  - Expert opinions and thought leadership
  - Current tools and technologies
  - Recent case studies and success stories
  - Industry statistics and trends

### Multi-Modal Content Per Week:
- Visual Elements: Describe diagrams, flowcharts, infographics needed for this week
- Interactive Components: Simulations, calculators, assessment tools for this week
- Multimedia: Videos, podcasts, interactive tutorials for this week
- Community Resources: Forums, discussion groups relevant to this week

### Current and Relevant Per Week:
- All examples must be from the last 2-3 years and relevant to this week's topic
- Include emerging trends and future predictions related to this week
- Reference current industry standards and best practices for this week's content
- Cite recent expert opinions specific to this week's subject matter

## 🎯 SPECIALIZED INSTRUCTIONS FOR WEEKLY PROCESSING

### For Technical Topics (Per Week):
- Include code examples with detailed explanations for this week's concepts
- Provide architecture diagrams and system designs relevant to this week
- Add performance benchmarks and comparisons for this week's tools/methods
- Include security considerations and best practices for this week's content

### For Business Topics (Per Week):
- Add ROI calculations and business impact metrics for this week's concepts
- Include strategic frameworks and decision matrices relevant to this week
- Provide implementation timelines and resource requirements for this week
- Add risk assessment and mitigation strategies for this week's content

### For Creative Topics (Per Week):
- Include design principles and aesthetic guidelines for this week
- Provide creative process workflows relevant to this week
- Add inspiration galleries and trend analysis for this week
- Include peer review and feedback frameworks for this week

## 🚀 KEY EXECUTION PRINCIPLES FOR WEEKLY PROCESSING

1. Process Sequentially: Complete one week entirely before moving to the next
2. Take Breaks: Always include the 10-second break indicator between weeks
3. Start with Problems: For each week, begin by explaining what problems that week's topic solves
4. Layer Explanations: Start simple, then add complexity throughout each week
5. Use Current Examples: All examples must be recent and relevant to each week's content
6. Multiple Perspectives: Provide technical, business, user viewpoints for each week's topic
7. Actionable Content: Each week must have practical application guidance
8. Stay Updated: Use Google Search extensively for each week's current information
9. Be Comprehensive: Cover each week's topic completely and thoroughly

CRITICAL: Process the course content week by week with 10-second breaks between each week. Transform each week's basic content into extraordinarily detailed educational materials using the problem-solution methodology.

Begin by identifying the total number of weeks, then start processing Week 1 with full depth and detail.
"""
)

# Create the deep content processing pipeline
deep_content_pipeline = LoopAgent(
    name="DeepContentPipeline", 
    sub_agents=[deep_course_content_Creator],
    description="Complete pipeline: planning → content generation → deep week-by-week content creation",
    max_iterations=2,
)

final_pipeline = SequentialAgent(
    name="FinalContentPipeline",
    sub_agents=[courseplanneragnt, content_refinement_loop, deep_content_pipeline],
    description="Final pipeline that combines course planning, content generation, and deep content creation.",
)

root_agent = final_pipeline

print("Course content generation pipeline has been successfully configured!")