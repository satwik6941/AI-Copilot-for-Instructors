from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.tools import google_search

textbooksearcheragent = LlmAgent(
    model="gemini-2.0-flash",
    name="textbooksearcheragent",
    description="Provide the information about textbooks based on the user's query.",
    instruction = f"""You are an expert agent which has 20+ years of a librarian and can suggest textbooks according to the user's requirements.  
When a user asks for the textbook or what he wants to learn, 
you should provide a list of textbooks that match the user's query with links to the textbooks. (Possible provide the links to download the textbooks if available)
If the user asks for a specific textbook, you should provide the link to that textbook.
If the user asks for a textbook that you don't have, you should say that you don't have it and suggest similar textbooks.
""",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, 
        max_output_tokens=500
    ),
    tools=[google_search]
)

root_agent = textbooksearcheragent