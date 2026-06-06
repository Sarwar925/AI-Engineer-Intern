from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

root_agent = Agent(
    model='gemini-2.5-flash-native-audio-preview-12-2025',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge and based on google search and answer in english only.if user prompts something then call the prompt_agent',
    tools=[google_search]
)

