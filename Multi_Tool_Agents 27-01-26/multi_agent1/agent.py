import datetime
import os
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # Essential for OpenAI support

# 1. Ensure your OpenAI API key is set in your environment
os.environ["OPENAI_API_KEY"] = "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"

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}.",
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    return {"status": "success", "report": report}

# 2. Define the model using LiteLlm wrapper
# Use "openai/gpt-4o" or "openai/gpt-3.5-turbo"
openai_model = LiteLlm(model="openai/gpt-4o")

# 3. Initialize the Agent with the correct model object
root_agent = LlmAgent(
    name="weather_time_agent",
    model=openai_model,  # Pass the LiteLlm object here
    description="Agent to answer questions about the time and weather in a city.",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
    tools=[get_weather, get_current_time],
)
