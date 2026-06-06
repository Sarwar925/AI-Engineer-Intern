import tweepy
import os

def post_tweet_tool(content: str):
    # Ensure you are using the v2 Client
    client = tweepy.Client(
        # For Free Tier, these 4 are still the core for posting
        consumer_key=os.getenv("nEsT8yNxaidAD0pS49tikaAYS"),
        consumer_secret=os.getenv("CB4oIsvlMAev1pIu7mYLqJdZKNNLLyHj33KZmoTupLQk3xtINq"),
        access_token=os.getenv("2019355308078878720-wwdcX7VK2fCzMQJMTFoVtt0AM5I68i"),
        access_token_secret=os.getenv("CVgkNasGpKBDSwTzN06yIATdh0Mg6gJMCowhPWtrhpz14")
    )
    
    try:
        response = client.create_tweet(text=content)
        return f"Posted! ID: {response.data['id']}"
    except tweepy.errors.Forbidden as e:
        return "Error: You might need to regenerate tokens with 'Write' permissions."
    except Exception as e:
        if "credits" in str(e).lower():
            return "Limit Reached: Your 500 free monthly posts are exhausted."
        return f"Technical Error: {e}"
post_tweet_tool("Hello from Tweepy v2!")