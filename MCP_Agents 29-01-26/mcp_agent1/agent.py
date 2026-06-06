from google.adk.agents import Agent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

HUGGING_FACE_TOKEN = "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"
openai_api_key = "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"
openai_model = LiteLlm(
    model="openai/gpt-4o",
    api_key=openai_api_key
)
root_agent = LlmAgent(
    model=openai_model,
    name="hugging_face_agent",
    instruction="Help users get information from Hugging Face",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://huggingface.co/mcp",
                headers={
                    "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
                },
            ),
        )
    ],
)


