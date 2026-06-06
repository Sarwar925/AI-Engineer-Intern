# # @title Import necessary libraries
# import os
# import asyncio
# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm # For multi-model support
# from google.adk.sessions import InMemorySessionService
# from google.adk.runners import Runner
# from google.genai import types # For creating message Content/Parts

# import warnings
# # Ignore all warnings
# warnings.filterwarnings("ignore")

# import logging
# logging.basicConfig(level=logging.ERROR)

# print("Libraries imported.")

import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService

# 1. SETUP
os.environ["OPENAI_API_KEY"] = "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" # Your key here
openai_model = LiteLlm(model="openai/gpt-4o")

# Tool1: Word Counter: Counts words and characters.
def count_words(text: str) -> dict:
    words = text.split()
    num_words = len(words)
    return {
        "word_count": num_words
    }
# Tool2: Word Finder: Finds the most common words (excluding "the", "a", etc.).
def find_word_in_text(text: str, word: str) -> dict:
    words = text.lower().split()
    for words in text.lower().split():
        if words == word.lower():
            print(f"The word '{word}' is present in the text.")
        else:
            print(f"The word '{word}' is NOT present in the text.")
    return {
        "word": word,
        "found": word.lower() in words
    }
# Tool3: Case Formatter: Switches text between UPPERCASE, lowercase, and Title Case.
def format_case(text: str, case_type: str) -> str:
    """
    Switches text between UPPERCASE, lowercase, and Title Case.
    
    Args:
        text (str): The string to format.
        case_type (str): The desired format ('uppercase', 'lowercase', or 'titlecase').
    """
    if case_type == "uppercase":
        return text.upper()
    elif case_type == "lowercase":
        return text.lower()
    elif case_type == "titlecase":
        return text.title()
    else:
        raise ValueError("Invalid case_type. Choose from 'uppercase', 'lowercase', or 'titlecase'.")

# 2. DEFINE WORKER AGENTS (No session_service here!)
analyst = LlmAgent(
    name="analyst",
    model=openai_model,
    description="Analyst for counting words.",
    instruction="Count words accurately.",
    tools=[count_words, find_word_in_text] # Simplified for example
)

formatter = LlmAgent(
    name="formatter",
    model=openai_model,
    description="Formatter for text casing.",
    instruction="Format text exactly as requested.",
    tools=[format_case]
)

# 3. THE ROOT AGENT
# REMOVE 'session_service=session_service' from here!
root_agent = LlmAgent(
    name="manager",
    model=openai_model,
    description="Routes tasks to analyst or formatter.",
    instruction="Delegate tasks. Use session memory to recall text from earlier.",
    sub_agents=[analyst, formatter]
)

# 4. HOW TO CONNECT THE MEMORY
# If you are running locally (without 'adk web'), you use a Runner:
from google.adk.runners import Runner

# The Runner is the one who 'owns' the session service
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent, 
    session_service=session_service,
    app_name="My_Multi_Agent_App"
)