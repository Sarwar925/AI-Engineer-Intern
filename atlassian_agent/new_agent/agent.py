from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Use the path you found in the terminal
CARTESIA_EXE = r"C:\Users\AL MAKKAH TRDERS\AppData\Local\Programs\Python\Python313\Scripts\cartesia-mcp.exe"
CARTESIA_API_KEY = "sk_car_5dNxnxCnzWECaurPg7MAfc"

root_agent = Agent(
    model="gemini-3-flash-preview", # Use a valid model name
    name="cartesia_agent",
    instruction="Help users generate speech and work with audio content",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=CARTESIA_EXE,
                    args=[], # No args needed when calling the exe directly
                    env={
                        "CARTESIA_API_KEY": CARTESIA_API_KEY,
                        # "OUTPUT_DIRECTORY": "./output",
                    }
                ),
                timeout=60, # Increased timeout to prevent TaskGroup sub-exceptions
            ),
        )
    ],
)

# Test the connection
# response = root_agent.chat("Can you list the available voices?")
# print(response)