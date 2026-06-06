from google.adk.agents import Agent

root_agent = Agent(
    model="gemini-1.5-flash",
    name="time_assistant",
    instruction="You are a helpful assistant. Use the get_current_datetime tool to get time"
)