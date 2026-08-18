import os
import imaplib
import smtplib
import email
import time
import logging
from email.mime.text import MIMEText
from dotenv import load_dotenv

from google.adk.agents import Agent
from openai import OpenAI

# ======================
# CONFIG
# ======================
load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHECK_INTERVAL = 15  # seconds

logging.basicConfig(level=logging.INFO)

# simple memory to avoid duplicate replies
PROCESSED_EMAILS = set()

# ======================
# SAFE EMAIL PARSER
# ======================
def extract_body(msg):
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors="ignore")
        else:
            return msg.get_payload(decode=True).decode(errors="ignore")
    except:
        return ""

# ======================
# TOOL: READ EMAILS
# ======================
# @tool
def read_emails() -> list:
    """
    Returns list of new emails:
    [{id, subject, body}]
    """
    results = []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()

        for e_id in email_ids:
            if e_id in PROCESSED_EMAILS:
                continue

            _, msg_data = mail.fetch(e_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            from_email = email.utils.parseaddr(msg["From"])[1]

            if from_email != TARGET_EMAIL:
                continue

            subject = msg.get("Subject", "")
            body = extract_body(msg)

            results.append({
                "id": e_id.decode(),
                "subject": subject,
                "body": body
            })

            PROCESSED_EMAILS.add(e_id)

        mail.logout()

    except Exception as e:
        logging.error(f"Read error: {e}")

    return results

# ======================
# TOOL: SEND EMAIL
# ======================
# @tool
def send_email(subject: str, reply_text: str) -> str:
    """
    Send reply email
    """
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)

        msg = MIMEText(reply_text)
        msg["From"] = EMAIL
        msg["To"] = TARGET_EMAIL
        msg["Subject"] = f"Re: {subject}"

        server.sendmail(EMAIL, TARGET_EMAIL, msg.as_string())
        server.quit()

        return "sent"

    except Exception as e:
        logging.error(f"Send error: {e}")
        return "failed"

# ======================
# AGENT
# ======================
agent = Agent(
    name="Production_Email_Agent",
    instruction="""
You are a professional AI email assistant.

Workflow:
1. Read unread emails using tool
2. If email exists, understand it
3. Generate professional reply
4. Send reply using tool

Rules:
- Be concise and polite
- Do not hallucinate
- If unclear, ask clarification
""",
    tools=[read_emails, send_email],
)

# ======================
# AGENT EXECUTION
# ======================
def process_emails():
    emails = read_emails()

    if not emails:
        logging.info("No new emails")
        return

    for e in emails:
        logging.info(f"Processing: {e['subject']}")

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an email assistant."},
                {"role": "user", "content": e["body"]}
            ]
        )

        reply = response.choices[0].message.content

        send_email(e["subject"], reply)

        logging.info("Replied successfully")

# ======================
# WORKER LOOP
# ======================
def run_worker():
    logging.info("🚀 Production Email Agent Running...")

    while True:
        try:
            process_emails()
        except Exception as e:
            logging.error(f"Worker error: {e}")

        time.sleep(CHECK_INTERVAL)

# ======================
# ENTRY
# ======================
if __name__ == "__main__":
    run_worker()