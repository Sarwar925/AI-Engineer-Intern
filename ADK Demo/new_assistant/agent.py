from google.adk.agents.llm_agent import Agent
from google.adk.agents import Agent
from datetime import datetime

def get_current_time() -> str:
    """
    Use this tool when the user asks for the current time or now time.
    Returns the current system time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[get_current_time]
)
