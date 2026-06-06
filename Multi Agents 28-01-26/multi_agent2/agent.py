# import os
# import requests
# import logging
# from google.adk.agents.llm_agent import LlmAgent
# from google.adk.models.lite_llm import LiteLlm

# # --- 2. ENVIRONMENT SETUP ---
# # CRITICAL: It is better to set these via your terminal or a .env file.
# # If you hardcode them, ensure they are exactly correct.
# os.environ["OPENAI_API_KEY"] = "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" 
# os.environ["WEATHER_API_KEY"] = "004ca9a64cde2577d678a74bf9cdb33a"

import os
import requests
import logging
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- 1. LOGGING SETUP ---
logger = logging.getLogger("AgentSystem")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("agent_system.log", mode='a', encoding='utf-8')
console_handler = logging.StreamHandler()

file_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --- 2. ENVIRONMENT SETUP ---
# Paste your API keys here
os.environ["OPENAI_API_KEY"] = "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"
os.environ["WEATHER_API_KEY"] = "004ca9a64cde2577d678a74bf9cdb33a"

# --- 3. TOOLS DEFINITION ---
def get_weather(city: str) -> str:
    """Fetches weather data using the FREE OpenWeather 2.5 API."""
    api_key = os.getenv("WEATHER_API_KEY")
    logger.info(f"Tool 'get_weather' triggered for city: {city}")

    # Use the 2.5 'weather' endpoint (Free) instead of '3.0/onecall' (Paid)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        # Log the full response for debugging
        logger.debug(f"Weather API Response: {data}")

        if response.status_code != 200:
            error_msg = data.get("message", "Unknown error")
            logger.error(f"Weather API Error: {error_msg}")
            return f"Error: {error_msg}"

        # Note the different JSON structure for the free API (data["main"] vs data["current"])
        temp_c = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        
        logger.info(f"Successfully retrieved weather for {city}: {temp_c}°C, {condition}")
        return f"The current weather in {city} is {condition} with a temperature of {temp_c}°C."

    except Exception as e:
        logger.exception("An unexpected error occurred in get_weather tool")
        return f"Failed to connect to weather service."

# --- 4. AGENT INITIALIZATION ---
openai_model = LiteLlm(model="openai/gpt-4o")

weather_agent = LlmAgent(
    model=openai_model,
    name='weather_agent',
    instruction='Always use the get_weather tool for current conditions.',
    tools=[get_weather],
)

root_agent = LlmAgent(
    model=openai_model,
    name='root_agent',
    instruction='Delegate weather questions to weather_agent.',
    sub_agents=[weather_agent],
)

# --- 5. EXECUTION ---
if __name__ == "__main__":
    query = "What is the current weather in Paris?"
    try:
        response = root_agent.run(query)
        print(f"\nFINAL ANSWER: {response}")
    except Exception as e:
        logger.error(f"Critical System Failure: {str(e)}")