import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # Ensure correct import path
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
import dotenv

dotenv.load_dotenv()

EXA_API_KEY = os.environ.get("EXA_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 1. Connect to the REMOTE specialist (The Shared Hub)
remote_params = StreamableHTTPConnectionParams(
    url="https://mcp.exa.ai/mcp", 
    headers={
        # FIXED: Use f-string to pass the actual variable value
        "Authorization": f"Bearer {EXA_API_KEY}" 
    }
)

# 2. Define the Model
# FIXED: Ensure LiteLlm knows it's an OpenAI model
openai_model = LiteLlm(model="openai/gpt-4o", api_key=OPENAI_API_KEY)

# 3. Define the Agent
# FIXED: Renamed to 'root_agent' for ADK CLI compatibility
root_agent = LlmAgent(
    name="ClientAgent",
    model=openai_model,
    instruction="""You are a Research Specialist. 
    Your goal is to find high-quality information from the web.
    Use the 'search' tool to find relevant URLs and 
    use 'get_contents' to read the full text of those pages.
    Always provide citations for the links you find.""",
    tools=[MCPToolset(connection_params=remote_params)]
)


