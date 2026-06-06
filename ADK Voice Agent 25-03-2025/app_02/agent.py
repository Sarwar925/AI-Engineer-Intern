import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import requests

load_dotenv()

# === CUSTOM TOOL: Post to LinkedIn ===
def post_to_linkedin(content: str) -> dict:
    """
    Posts the given text content to LinkedIn as a public UGC post.
    
    Args:
        content (str): The text you want to post on LinkedIn.
    
    Returns:
        dict: Status and post ID or error message.
    """
    access_token = os.getenv("LINKEDIN_TOKEN")
    person_urn = os.getenv("AUTHOR_URN")
    
    if not access_token or not person_urn:
        return {"status": "error", "message": "LinkedIn credentials not configured"}
    
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        post_id = response.headers.get("x-restli-id") or response.json().get("id")
        return {
            "status": "success",
            "message": "Posted successfully to LinkedIn!",
            "post_id": post_id
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"LinkedIn API error: {str(e)}"
        }

# Wrap as ADK FunctionTool (automatic schema from docstring + type hints)
linkedin_tool = FunctionTool(func=post_to_linkedin)

root_agent = Agent(
    name="linkedin_voice_poster",
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    tools=[linkedin_tool],
    instruction="""
    You are an expert Social Media Manager and Content Creator.
    
    When a user asks you to "post about [topic]" or "post to LinkedIn: [topic]", follow these steps:
    1. RESEARCH & GENERATE: Do not post the user's short prompt. Instead, write a 
       professional, engaging, and insightful LinkedIn post about that topic.
    2. STRUCTURE: Use a hook, 2-3 bullet points or paragraphs of explanation, 
       and relevant hashtags (e.g., #MachineLearning #AI).
    3. CONFIRM: Read the generated post back to the user via voice and ask: 
       "Would you like me to post this to LinkedIn?"
    4. EXECUTE: Only call the post_to_linkedin tool AFTER the user gives 
       verbal confirmation.
    
    Speak naturally. If the topic is technical (like Machine Learning), 
    ensure the explanation is accurate but easy to read.
    """,
    description="Professional voice agent that generates and posts LinkedIn content."
)


