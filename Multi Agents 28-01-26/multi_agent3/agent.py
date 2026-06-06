from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search
from google.adk.agents import Agent
import os
# --- 0. IMPORTS & ENVIRONMENT SETUP ---
openai_model = LiteLlm(model="openai/gpt-4o")
os.environ["OPENAI_API_KEY"] = "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"
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCdzKnGkFIHbZ_m8MMJjc6gAPiFcFjl_ZU'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'FALSE'
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search

# --- 0. ENVIRONMENT SETUP ---
openai_model = LiteLlm(model="openai/gpt-4o")
# Gemini model for the Reviewer/Root functionality
gemini_model = LiteLlm(model="google/gemini-2.5-flash") 

# --- 1. AGENT DEFINITIONS (Bottom-Up) ---

# First: The Writer (Grandchild)
writer_agent = LlmAgent(
    model=openai_model,
    name='writer_agent',
    description='An agent that writes content based on user prompts.',
    instruction='Generate well-structured and engaging content.'
)

# Second: The Reviewer (Child / Sub-Manager)
# We nest the writer_agent INSIDE here.
reviewer_agent = LlmAgent(
    model=gemini_model,
    name='reviewer_agent', 
    description='An assistant that can write content and check weather.',
    instruction=(
        "1. Delegate content writing tasks to your sub-agent: writer_agent. "
        "2. Use the google_search tool to check weather. "
        "3. Review and update plans based on that weather."
    ),
    tools=[google_search],
    sub_agents=[writer_agent] # Writer now belongs to Reviewer
)

# Third: The Root Agent (The only entry point)
# We ONLY add the reviewer_agent here.
root_agent = LlmAgent(
    model=openai_model,
    name='root_agent',
    description='Main entry point for user questions.',
    instruction='Answer user questions. Delegate complex tasks to the reviewer_agent.',
    sub_agents=[reviewer_agent] # DO NOT add writer_agent here again!
)

# --- 2. EXECUTION ---
if __name__ == "__main__":
    query = "Write a travel plan for Lahore and check if the weather is good for outdoor tours."
    # Calling the root will now flow: Root -> Reviewer -> Writer
    response = root_agent.run(query)
    print(response)
