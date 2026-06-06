from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


# Use the path you found in the terminal
# CARTESIA_EXE = r"C:\Users\AL MAKKAH TRDERS\AppData\Local\Programs\Python\Python313\Scripts\cartesia-mcp.exe"
CARTESIA_API_KEY = "sk_car_5dNxnxCnzWECaurPg7MAfc"
root_agent = Agent(
    model='',
    name="new_agent",
    instruction="",
    description="",
    tools=[
        MCPToolset(
            connection_params = StdioConnectionParams(
                server_params=StdioServerParameters(
                    # command=CARTESIA_EXE,
                    args=[],
                    env={
                        "CARTESIA_API_KEY":CARTESIA_API_KEY
                    }
                )
            )
        )
    ]
)