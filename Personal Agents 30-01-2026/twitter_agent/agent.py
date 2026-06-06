from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import LiteLlm
import tweepy
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Tool to post a tweet
def post_tweet_tool(content: str):
    """First tell me the environment variables are loaded and working successfully and then posts a message to X (Twitter)."""
    import os
    from dotenv import load_dotenv
    load_dotenv() # MUST be here to read the .env file
    
    # Debug: Check if keys are actually found
    if not os.getenv("X_API_KEY"):
        return "Error: Environment variables not loaded. Check your .env file."

    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
        # client_id=os.getenv("X_CLIENT_ID"),
        # client_secret=os.getenv("X_CLIENT_SECRET")
    )
    print("Environment variables loaded successfully.")
    try:
        response = client.create_tweet(text=content)
        return f"Successfully posted! Tweet ID: {response.data['id']}"
    except Exception as e:
        return f"Failed to post. Technical Error: {e}"

api_model = LiteLlm(
    model='gpt-4o',
    api_key=OPENAI_API_KEY)
root_agent = LlmAgent(
    model=api_model,
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge and if user says post on twitter, give a draft post and if he confirms then post on tweet and say posted successfully.',
    tools=[post_tweet_tool],
)
