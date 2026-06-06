from google.adk.agents import Agent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams



#--------- Hugging Face Agent ---------#
HUGGING_FACE_TOKEN = "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"
openai_api_key = "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"
openai_model = LiteLlm(
    model="openai/gpt-4o",
    api_key=openai_api_key
)
huggingface_agent = LlmAgent(
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


# ---------- Cartesian Agent ---------#
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
CARTESIA_API_KEY = "sk_car_5dNxnxCnzWECaurPg7MAfc"
CARTESIA_EXE = r"C:\Users\AL MAKKAH TRDERS\AppData\Local\Programs\Python\Python313\Scripts\cartesia-mcp.exe"

cartesia_agent = Agent(
    model='',
    name="cartesian_agent",
    instruction="You are a professional Voice Synthesis Specialist. Your sole purpose is to convert provided text into high-quality, lifelike speech using your audio tools. Do not answer general questions; instead, take the input text and generate the corresponding audio output. You must select the most appropriate voice ID based on the context of the text (e.g., professional for news, friendly for conversation) and ensure the speech is expressive and clear. If a specific voice is requested, prioritize that voice ID.",
    description="Use this agent whenever you need to convert text information into audio or spoken word. This agent is capable of generating ultra-fast, lifelike speech in multiple languages and tones. Ideal for reading search results, summarizing articles out loud, or providing vocal responses to the user.",
    tools=[
        MCPToolset(
            connection_params = StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=CARTESIA_EXE,
                    args=[],
                    env={
                        "CARTESIA_API_KEY":CARTESIA_API_KEY
                    }
                )
            )
        )
    ]
)



# ----------- Root Agent ----------#
root_agent = Agent(name="root_agent",
                   model='',
                   instruction="""You are the Lead Orchestrator of a multi-agent AI team. Your role is to analyze user prompts and delegate tasks to your specialized worker agents:
                        Use the hugging_face_agent for any requests involving searching, exploring, or getting details about AI models, datasets, or spaces.
                        Use the voice_specialist (Cartesia) whenever the user asks for a spoken response, audio generation, or for information to be read aloud.
                        Workflow Integration: If a user asks to 'find a model and tell me about it,' first call the hugging_face_agent to get the details, and then pass those details to the voice_specialist to generate the audio.
                        Always summarize technical data into a conversational format before sending it to the voice_specialist.""",
                   description="The root agent delegates tasks to specialized agents and integrates their outputs.",
                   sub_agents=[huggingface_agent, cartesia_agent]
                )