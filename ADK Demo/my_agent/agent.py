from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from google.adk.code_executors import BuiltInCodeExecutor

APP_NAME = "google_search_agent"
USER_ID = "user1234"
SESSION_ID = "1234"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    code_executor=BuiltInCodeExecutor(),
    tools=[google_search]
)
