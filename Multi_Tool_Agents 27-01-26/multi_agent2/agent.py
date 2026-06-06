from google.adk.agents.llm_agent import LlmAgent
import os
from google.adk.models.lite_llm import LiteLlm  # Essential for OpenAI support
os.environ["OPENAI_API_KEY"] = "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"

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

openai_model = LiteLlm(model="openai/gpt-4o")
root_agent = LlmAgent(
    model=openai_model,
    name='The_Content_Analyst_Agent',
    description='A multi-tool agent for text analysis and formatting',
    instruction='You have access to multiple tools for analyzing and formatting text. Use them as needed based on user requests.',
    tools=[count_words,find_word_in_text,format_case]
)
