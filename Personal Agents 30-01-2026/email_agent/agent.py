import smtplib
from email.message import EmailMessage
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
openai_api_key = "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"
openai_model = LiteLlm(
    model="openai/gpt-4o",
    api_key=openai_api_key
)
# 1. Your Tool Function
def send_email_tool(recipient: str, subject: str, body: str):
    """Sends an email to a specified recipient with a subject and body."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "cena99398@gmail.com"
    msg['To'] = recipient

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("cena99398@gmail.com", "adzd wnpm scjk njpt")
        smtp.send_message(msg)
    return "Email sent successfully!"

# 2. THE FIX: Change the variable name to 'root_agent'
root_agent = LlmAgent(
    name="Email_Assistant",
    model=openai_model,
    instruction="You are a professional email assistant. Draft and send emails using tools.",
    tools=[send_email_tool]
)