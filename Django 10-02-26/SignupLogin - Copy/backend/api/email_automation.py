import email
import imaplib
import logging
import os
import smtplib
import asyncio
from functools import partial

from dotenv import load_dotenv
from email.mime.text import MIMEText

# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
PROCESSED = set()
session_service = InMemorySessionService()

logging.basicConfig(level=logging.INFO)

def extract_body(msg):
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode(errors="ignore")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                return payload.decode(errors="ignore")
    except Exception:
        return ""
    return ""


def read_emails_tool(email_account: str, app_password: str):
    results = []
    if not email_account or not app_password:
        return "Error: Missing credentials"

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_account, app_password)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK":
            return []

        email_ids = messages[0].split()
        # Process only the oldest 3 unread to prevent overloading the agent in one run
        for e_id in email_ids[:3]:
            eid = e_id.decode()
            if eid in PROCESSED:
                continue

            _, msg_data = mail.fetch(e_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            results.append({
                "from": email.utils.parseaddr(msg.get("From"))[1],
                "subject": msg.get("Subject", ""),
                "body": extract_body(msg),
                "thread_id": msg.get("In-Reply-To") or msg.get("Message-ID", ""),
            })
            PROCESSED.add(eid)
        mail.logout()
    except Exception as e:
        return f"Error reading emails: {e}"
    return results


def send_email_tool(email_account, app_password, to, subject, reply_text, thread_id):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_account, app_password)

        msg = MIMEText(reply_text)
        msg["From"] = email_account
        msg["To"] = to
        msg["Subject"] = f"Re: {subject}"
        msg["In-Reply-To"] = thread_id
        msg["References"] = thread_id

        server.sendmail(email_account, to, msg.as_string())
        server.quit()
        return "Success: Email sent"
    except Exception as e:
        return f"Error sending email: {e}"

def process_email_batch(email_account=None, app_password=None):
    # Setup credentials
    acc = email_account or os.getenv("EMAIL")
    pwd = app_password or os.getenv("APP_PASSWORD")
    
    if not acc or not pwd:
        return {"success": False, "error": "Email credentials missing"}

    # 1. Fetch unread emails first to see if we even need the agent
    # This prevents unnecessary LLM calls if the inbox is empty
    unread_list = read_emails_tool(acc, pwd)
    if not unread_list or (isinstance(unread_list, list) and len(unread_list) == 0):
        return {"success": True, "agent_summary": "No unread emails found."}
    
    if isinstance(unread_list, str) and unread_list.startswith("Error"):
         return {"success": False, "error": unread_list}

    # 2. Define tools for the agent
    def read_emails_agent():
        """Fetch unseen emails from the inbox."""
        return unread_list

    def send_email_agent(to: str, subject: str, reply_text: str, thread_id: str):
        """Send a professional reply. thread_id is required to keep the conversation linked."""
        return send_email_tool(email_account=acc, app_password=pwd, to=to, subject=subject, reply_text=reply_text, thread_id=thread_id)

    agent = LlmAgent(
        model=LiteLlm(model="openai/gpt-4o-mini", api_key=OPENAI_API_KEY),
        name="email_automation_agent",
        instruction="""You are an automated email assistant. Follow these steps:
        1. Use read_emails_agent to get unread messages.
        2. For each message:
           a. Classify as 'support', 'sales', or 'spam'.
           b. If 'spam', ignore it.
           c. If 'support' or 'sales', draft ONE professional reply. 
           d. Send the reply using send_email_agent immediately.
        3. IMPORTANT: Do not reply to the same email twice.
        4. Provide a final bulleted summary of your actions.""",
        tools=[read_emails_agent, send_email_agent]
    )

    runner = Runner(app_name="email_auto", agent=agent, session_service=session_service)
    
    # Execute in a session
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    session_obj = loop.run_until_complete(session_service.create_session(user_id=acc, app_name="email_auto"))
    prompt = Content(role="user", parts=[Part(text="Process my unread emails.")])
    
    events = runner.run(user_id=acc, session_id=session_obj.id, new_message=prompt)

    final_log = ""
    for event in events:
        if event.is_final_response():
            final_log = event.content.parts[0].text

    return {
        "success": True,
        "agent_summary": final_log
    }
