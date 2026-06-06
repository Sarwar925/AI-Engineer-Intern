from google.adk.agents import Agent
from google.adk.tools import tools
from datetime import datetime
APP_NAME = "google_search_agent"

def time_now():
    return datetime.now()
root_agent = Agent(
    model='gemini-2.5-flash',
    name='time_now',
    instruction='You are an assistant which get user input and gives output to the user on the base of input',
    description='Please do work properly',
    tools=[time_now()]
)