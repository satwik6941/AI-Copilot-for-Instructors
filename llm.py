from google import genai
from dotenv import load_dotenv
import os
import pathlib
from google.genai import types

load_dotenv()

difficulty_level = input("Enter the difficulty level (beginner, intermediate, advanced): ")
if difficulty_level.lower() in ['none',''] or difficulty_level.lower() not in ['beginner', 'intermediate', 'advanced']:
    difficulty_level = "beginner"  # Default to beginner if none specified

while True:
    duration = input("Enter the desired duration for the course (e.g., 4 weeks, 8 weeks): ")
    if duration == "" or duration.lower() == "none":
        print("Duration cannot be empty. Please enter a valid duration.")
    else:
        break

teaching_style = input("Enter preferred teaching style (e.g., hands-on, theoretical, project-based): ")
if teaching_style.lower() == "none":
    teaching_style = "theoretical"  # Default to theoretical if none specified

print("Thank you for providing the inputs. Processing your request...")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Configure Google Search as a tool for grounding
google_search_tool = genai.types.Tool(
    google_search=genai.types.GoogleSearch()
)

system_prompt = """You are a course design assistant.

You will be given two main inputs:
1. A user query describing what they want to learn or their educational goals
2. A curriculum PDF document containing existing course materials, syllabi, or educational content

Your task is to:
1. **Analyze the user input** to understand:
    - The specific learning topic or subject area they're interested in
    - Their educational goals and objectives
    - Any implied difficulty level or target audience
    - Preferred learning style or approach (if mentioned)

2. **Analyze the curriculum PDF** to extract:
    - Existing course structure and organization
    - Key topics and concepts covered
    - Learning objectives and outcomes
    - Assessment methods and activities
    - Resource recommendations
    - Teaching methodologies used

3. **Synthesize both inputs** to create a comprehensive course design that:
    - Aligns the user's learning goals with relevant content from the curriculum
    - Creates a modular course outline with weekly or unit-based structure
    - Adapts the existing curriculum content to match the user's specific interests

4. **For each module, provide:**
    - Clear learning goals and key concepts
    - Engaging activities and instructional methods
    - High-quality, up-to-date online resources using real-time Google search (include web links and descriptions)
    - Integration of relevant content from the provided curriculum PDF

5. **Format your output** in readable **Markdown** with proper headers, bullets, and clear organization

6. **Adapt the content** based on:
    - The user's apparent experience level (beginner, intermediate, advanced)
    - Learning preferences inferred from their query
    - Best practices for effective online and self-directed learning

7. **At the end of your output, generate a specialized system prompt** designed for an AI teaching agent that will:
    - Use the course outline you've created to guide learners
    - Answer questions about the specific topics covered
    - Generate supplementary study materials and exercises
    - Provide personalized learning support based on the curriculum

Ensure your analysis is thorough and your course design effectively bridges the user's learning needs with the educational content available in the curriculum PDF. Use real-time search to supplement with current, relevant resources.

Respond only after carefully analyzing both the user input and the curriculum document."""
try:
    filepath = pathlib.Path(r"C:\Users\hi\Documents\My works and PPTs\Copilot For Instructors\curriculum.pdf")
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[teaching_style, duration, difficulty_level,
                    types.Part.from_bytes(
                        data=filepath.read_bytes(),
                        mime_type='application/pdf',
                    )],
        config=genai.types.GenerateContentConfig(
            tools=[google_search_tool],
            system_instruction=system_prompt,
        ),
    )

    print(response.text)
    
    # Save the response to a text file for the master agent
    output_file_path = r"C:\Users\hi\Documents\My works and PPTs\Copilot For Instructors\planner_agent_instruction.txt"
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\nResponse saved to: {output_file_path}")
    except Exception as e:
        print(f"Error saving response to file: {e}")

    # Optional: Print grounding metadata if available
    if response.candidates:
        for candidate in response.candidates:
            if candidate.grounding_metadata and candidate.grounding_metadata.web_search_queries:
                print("\n--- Grounding Metadata ---")
                print("Web Search Queries:", candidate.grounding_metadata.web_search_queries)
                if candidate.grounding_metadata.grounding_chunks:
                    print("Grounding Chunks (Web):")
                    for chunk in candidate.grounding_metadata.grounding_chunks:
                        if chunk.web:
                            print(f"  - Title: {chunk.web.title}, URL: {chunk.web.uri}")
except Exception as e:
    print(f"An error occurred during LLM interaction: {e}")
else:
    print("Could not load input data for the LLM.")