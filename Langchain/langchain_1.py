import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

# 1. Setup API Key
os.environ["OPENAI_API_KEY"] = "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"

# 2. Define tools properly
@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# 3. Initialize the specific OpenAI model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 4. Create the agent using the model object
agent = create_agent(
    model=model, 
    tools=[get_weather],
    system_prompt="You are a helpful assistant"
)

# 5. Run the agent
result = agent.invoke({"messages": [{"role": "user", "content": "what is the weather in sf"}]})
print(result["messages"][-1].content)