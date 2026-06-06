from __future__ import annotations
import os
from google.adk.agents import Agent
import dotenv
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
root_agent = Agent(
    name="wc_woocommerce_agent",
    model=os.getenv('openai/gpt-4o'),
    description="Real-time WooCommerce database agent",
    instruction=(
        "You are a real-time WooCommerce assistant.\n"
        "For every question about orders, products, stock, customers, shipping, or sales, "
        "you must call the live_woocommerce_lookup tool first and answer only from its result.\n"
        "If the tool asks for clarification, ask the user for that missing detail.\n"
        "Do not guess, do not hallucinate, and do not answer from memory when store data is requested."
    ),
    tools=[],
)
