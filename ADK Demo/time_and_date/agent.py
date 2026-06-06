
from google.adk.agents import Agent


# 2. Attach the tool to your agent
time_agent = Agent(
    name="time_assistant",
    model="gemini-1.5-flash",
    instruction="You are a helpful assistant. Use the get_current_datetime tool to answer time-related questions.",
)
