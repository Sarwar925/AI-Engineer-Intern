# Working fine

import os
from google.adk.agents import LlmAgent
# from google.adk.models import LiteLlm
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- 1. Configuration ---
# Use the standard name or your custom name, but ensure it matches your .env file
API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
AUTHOR_URN = os.environ.get("AUTHOR_URN")

# --- 2. Define Models ---
# Use one strong general model for both text and voice.
chat_model_engine = LiteLlm(model="openai/gpt-4o", api_key=API_KEY)

GENERAL_ASSISTANT_INSTRUCTION = """
You are a helpful assistant.
Answer the user's question directly and clearly.
Use tools only when the user explicitly asks for LinkedIn, email, or image generation.
For normal questions, respond naturally and concisely.
Response only in English.
""".strip()

# --- 3. Tools ---
def generate_image(prompt):
    import requests
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)
    response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", n=1)
    image_url = response.data[0].url
    img_path = os.path.join(settings.MEDIA_ROOT, "ai_post_image.png")
    img_data = requests.get(image_url).content
    with open(img_path, 'wb') as f:
        f.write(img_data)
    return img_path

def post_to_linkedin_action(text_content: str, image_path: str = "ai_post_image.png") -> str:
    import requests
    api_headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}", "X-Restli-Protocol-Version": "2.0.0", "Content-Type": "application/json"}
    try:
        reg_res = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", headers=api_headers, json={
            "registerUploadRequest": {"recipes": ["urn:li:digitalmediaRecipe:feedshare-image"], "owner": AUTHOR_URN,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]}
        }).json()
        upload_url = reg_res['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_id = reg_res['value']['asset']
        with open(image_path, 'rb') as f:
            requests.put(upload_url, data=f, headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"})
        payload = {"author": AUTHOR_URN, "lifecycleState": "PUBLISHED", "specificContent": {"com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": text_content}, "shareMediaCategory": "IMAGE", "media": [{"status": "READY", "media": asset_id}]
        }}, "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}}
        res = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=api_headers, json=payload)
        return "SUCCESS: Post live." if res.status_code == 201 else f"Fail: {res.text}"
    except Exception as e: return f"LinkedIn Error: {e}"

def send_email_tool(recipient: str, subject: str, body: str):
    import smtplib
    from email.message import EmailMessage
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = ""
    msg['To'] = recipient
    img_path = os.path.join(settings.MEDIA_ROOT, "ai_post_image.png")
    if os.path.exists(img_path):
        with open(img_path, 'rb') as img:
            msg.add_attachment(img.read(), maintype='image', subtype='png', filename="ai_post_image.png")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("", "")
            smtp.send_message(msg)
        return "Email sent successfully!"
    except Exception as e: return f"Email Error: {e}"

# --- 4. Agent Factory ---
def get_agent(mode="text"):
    return LlmAgent(
        model=chat_model_engine,
        name=f'social_{mode}_agent',
        instruction=GENERAL_ASSISTANT_INSTRUCTION,
        tools=[send_email_tool, post_to_linkedin_action, generate_image]
    )

root_agent = LlmAgent(
    model=chat_model_engine,
    name='root_agent',
    instruction=GENERAL_ASSISTANT_INSTRUCTION,
    tools=[send_email_tool, post_to_linkedin_action, generate_image]
)
# Minimal in-memory session service
session_service = InMemorySessionService()
# Runner
runner = Runner(
    app_name="django_chat_app",
    agent=root_agent,
    session_service=session_service
)








