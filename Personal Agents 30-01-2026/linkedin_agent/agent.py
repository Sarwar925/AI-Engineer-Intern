from google.adk.models import LiteLlm
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
import requests
# --- STEP 1: Define the LinkedIn Action as a Tool ---
def post_to_linkedin_action(text_content: str) -> str:
    """
    Publishes a text post to the user's LinkedIn profile.
    Args:
        text_content: The actual text of the post to be published.
    """
    # Use environment variables for security
    ACCESS_TOKEN = "AQXp-NrSvD29pLJ3jBFWBosiHKejONFDe_5eKUwB6MwK_5HrXC4USP_KGcOg4UIzr_spfpHRu2_eKsN-rVRUFhd3XWpvzRjnHMlGSiR0C6uCU3Vd4p38dZkMcBGLUbXVvbzzg4W2Bl7ERI2Dccy6h6noBjOksvNeqybz3kfMkLGZOkFoqU5jaZEN7fa-RsB36hPJjnubQ6GSyWE6lrOZK2rlMtK2CIg_lLemgpmidqkhfYQPLRatSZhhrA9jx9SZbsUBj692EFzsLqikswSz-muvoeoK4fnSumqk5xRSb94dLPMGIa9N17xLeq5bMmbjYW3QRBhMogiMUvtmcsZa00FMak27EA"
    AUTHOR_URN = "urn:li:person:hbpzZRp4Js"
    url = "https://api.linkedin.com/rest/posts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "LinkedIn-Version": "202601",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": AUTHOR_URN,
        "commentary": text_content,
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED"},
        "lifecycleState": "PUBLISHED",
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        return "SUCCESS: Post is live on LinkedIn."
    return f"ERROR: {response.status_code} - {response.text}"
# Convert the Python function into a formal ADK Tool
linkedin_tool = FunctionTool(post_to_linkedin_action)
openai_api_key = "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"
openai_model = LiteLlm(
    model="openai/gpt-4o",
    api_key=openai_api_key
)
# --- STEP 2: Define the ADK Agent ---
root_agent = LlmAgent(
    name="nexus_personal_agent",
    model=openai_model, # High-speed reasoning model
    instruction="""
        You are a social media manager for Nexus AI Systems.
        When the user gives you a topic, draft a professional post.
        ALWAYS ask for approval before using the post_to_linkedin_action tool.
        Once approved, call the tool with the exact text.
    """,
    tools=[post_to_linkedin_action]
)