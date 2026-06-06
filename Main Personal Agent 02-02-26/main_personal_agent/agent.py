from google.adk.models import LiteLlm
from google.adk.agents.llm_agent import LlmAgent
from openai import OpenAI
import requests
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
load_dotenv()
# 2. Configuration (Keys & IDs)
OPENAI_KEY = os.environ.get("OPENAI_KEY") # Your Key
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")  # Your Token
AUTHOR_URN = os.environ.get("AUTHOR_URN")

client = OpenAI(api_key=OPENAI_KEY)

# ------------- Tool 1: Image Generation ---------------
def generate_image(prompt: str) -> str:
    """Generates an image and returns the local file path."""
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1
    )
    image_url = response.data[0].url       
    # Download and Save
    img_path = "ai_post_image.png"
    img_data = requests.get(image_url).content
    with open(img_path, 'wb') as f:
        f.write(img_data)
    return img_path
# ------------- Tool 2: LinkedIn Posting ---------------
def post_to_linkedin_action(text_content: str, image_path: str = "ai_post_image.png") -> str:
    """Posts an image and text to LinkedIn."""
    
    api_headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Register Upload
        reg_res = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=api_headers,
            json={
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": AUTHOR_URN,
                    "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
                }
            }
        ).json()
        
        upload_url = reg_res['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_id = reg_res['value']['asset']

        # Step 2: Upload Binary
        with open(image_path, 'rb') as f:
            requests.put(upload_url, data=f, headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"})

        # Step 3: Create Post
        payload = {
            "author": AUTHOR_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text_content},
                    "shareMediaCategory": "IMAGE",
                    "media": [{"status": "READY", "media": asset_id}]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        res = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=api_headers, json=payload)
        
        return "SUCCESS: Post is live on LinkedIn." if res.status_code == 201 else f"Fail: {res.text}"
    except Exception as e:
        return f"LinkedIn Error: {e}"
# ------------- Tool 3: Email Tool -----------------
def send_email_tool(recipient: str, subject: str, body: str):
    """Sends an email. and if a user say send image then attach the generated image only one time don't add image more that one"""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "cena99398@gmail.com"
    msg['To'] = recipient
    #read the generated image and attach it
    with open("ai_post_image.png", 'rb') as img:
        img_data = img.read()
        msg.add_attachment(img_data, maintype='image', subtype='png', filename='ai_post_image.png')
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("cena99398@gmail.com", "adzd wnpm scjk njpt")
            smtp.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Email Error: {e}"

# ------------- Model & Agent Setup --------------
openai_model = LiteLlm(model="openai/gpt-4o", api_key=OPENAI_KEY)

root_agent = LlmAgent(
    model=openai_model,
    name='root_agent',
    instruction="""
    You are a social media assistant. 
    1. If the user wants a LinkedIn post,if he says generate image then ALWAYS call 'generate_image' first.
    2. Once you have the image path, show the user the image name and the text you plan to post.
    3. AFTER user confirms, call 'post_to_linkedin_action' and pass the 'image_path' you received from the first tool.
    4. Follow the same confirmation flow for emails.
    """,
    tools=[send_email_tool, post_to_linkedin_action, generate_image]
)

