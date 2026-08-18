# import os
# import imaplib
# import smtplib
# import email
# import time
# import logging
# from email.mime.text import MIMEText
# from dotenv import load_dotenv

# import dotenv
# from openai import OpenAI

# # ======================
# # CONFIG
# # ======================
# load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# EMAIL = os.environ.get("EMAIL")
# APP_PASSWORD = os.environ.get("APP_PASSWORD")

# raw_emails = os.environ.get("TARGET_EMAILS")

# if not raw_emails:
#     logging.warning("⚠️ TARGET_EMAILS not found in environment!")
#     TARGET_EMAILS = []
# else:
#     TARGET_EMAILS = [e.strip().lower() for e in raw_emails.split(",") if e.strip()]

# print("Final TARGET_EMAILS:", TARGET_EMAILS)


# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# CHECK_INTERVAL = 15

# logging.basicConfig(level=logging.INFO)

# PROCESSED_EMAILS = set()

# # ======================
# # SAFE EMAIL PARSER
# # ======================
# def extract_body(msg):
#     try:
#         if msg.is_multipart():
#             for part in msg.walk():
#                 if part.get_content_type() == "text/plain":
#                     return part.get_payload(decode=True).decode(errors="ignore")
#         else:
#             return msg.get_payload(decode=True).decode(errors="ignore")
#     except:
#         return ""

# # ======================
# # READ EMAILS
# # ======================
# def read_emails():
#     results = []

#     try:
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         mail.login(EMAIL, APP_PASSWORD)
#         mail.select("inbox")

#         status, messages = mail.search(None, '(UNSEEN)')
#         email_ids = messages[0].split()

#         for e_id in email_ids:
#             eid = e_id.decode()

#             if eid in PROCESSED_EMAILS:
#                 continue

#             _, msg_data = mail.fetch(e_id, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             from_email = email.utils.parseaddr(msg.get("From", ""))[1].lower().strip()

#             logging.info(f"Incoming email from: {from_email}")
#             logging.info(f"Allowed emails: {TARGET_EMAILS}")

#             # Filter allowed users
#             if from_email not in TARGET_EMAILS:
#                 logging.info(f"Skipped email from {from_email}")
#                 continue

#             subject = msg.get("Subject", "")
#             body = extract_body(msg)

#             results.append({
#                 "id": eid,
#                 "from": from_email,
#                 "subject": subject,
#                 "body": body
#             })

#             PROCESSED_EMAILS.add(eid)

#         mail.logout()

#     except Exception as e:
#         logging.error(f"Read error: {e}")

#     return results

# # ======================
# # SEND EMAIL
# # ======================
# def send_email(to_email: str, subject: str, reply_text: str):
#     try:
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(EMAIL, APP_PASSWORD)

#         msg = MIMEText(reply_text)
#         msg["From"] = EMAIL
#         msg["To"] = to_email
#         msg["Subject"] = f"Re: {subject}"

#         server.sendmail(EMAIL, to_email, msg.as_string())
#         server.quit()

#         return "sent"

#     except Exception as e:
#         logging.error(f"Send error: {e}")
#         return "failed"

# # ======================
# # PROCESS EMAILS
# # ======================
# def process_emails():
#     emails = read_emails()

#     if not emails:
#         logging.info("No new emails")
#         return

#     for e in emails:
#         logging.info(f"Processing from {e['from']} | Subject: {e['subject']}")

#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4.1-mini",
#                 messages=[
#                     {"role": "system", "content": "You are a professional email assistant."},
#                     {"role": "user", "content": e["body"]}
#                 ]
#             )

#             reply = response.choices[0].message.content

#             send_email(e["from"], e["subject"], reply)

#             logging.info(f"Replied to {e['from']} successfully")

#         except Exception as err:
#             logging.error(f"Processing error: {err}")

# # ======================
# # WORKER LOOP
# # ======================
# def run_worker():
#     logging.info("🚀 Multi-User Email Agent Running...")

#     while True:
#         try:
#             process_emails()
#         except Exception as e:
#             logging.error(f"Worker error: {e}")

#         time.sleep(CHECK_INTERVAL)

# # ======================
# # ENTRY
# # ======================
# if __name__ == "__main__":
#     run_worker()






















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
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMAIL = os.environ.get("EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")

raw_emails = os.environ.get("TARGET_EMAILS")

if not raw_emails:
    logging.warning("⚠️ TARGET_EMAILS not found!")
    TARGET_EMAILS = []
else:
    TARGET_EMAILS = [e.strip().lower() for e in raw_emails.split(",") if e.strip()]

CHECK_INTERVAL = 15
logging.basicConfig(level=logging.INFO)

PROCESSED_EMAILS = set()

# ======================
# PARSER
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
def read_emails() -> list:
    """Fetch unread emails from allowed users"""
    results = []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()

        for e_id in email_ids:
            eid = e_id.decode()

            if eid in PROCESSED_EMAILS:
                continue

            _, msg_data = mail.fetch(e_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            from_email = email.utils.parseaddr(msg.get("From", ""))[1].lower().strip()

            if from_email not in TARGET_EMAILS:
                continue

            subject = msg.get("Subject", "")
            body = extract_body(msg)

            results.append({
                "id": eid,
                "from": from_email,
                "subject": subject,
                "body": body
            })

            PROCESSED_EMAILS.add(eid)

        mail.logout()

    except Exception as e:
        logging.error(f"Read error: {e}")

    return results

# ======================
# TOOL: SEND EMAIL
# ======================
def send_email(to_email: str, subject: str, reply_text: str) -> str:
    """Send reply email"""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)

        msg = MIMEText(reply_text)
        msg["From"] = EMAIL
        msg["To"] = to_email
        msg["Subject"] = f"Re: {subject}"

        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()

        return "sent"

    except Exception as e:
        logging.error(f"Send error: {e}")
        return "failed"

# ======================
# AGENT
# ======================
agent = Agent(
    name="Multi_User_Email_Agent",
    instruction="""
You are a professional AI email assistant. Reply like a human, but be concise and to the point. You will be given emails from multiple users. Only reply to the provided emails and do not hallucinate any information.

Instructions:

Workflow:
1. Call read_emails
2. If emails exist:
   - Understand each email
   - Generate a professional reply
   - Call send_email with correct parameters

Rules:
- Be polite and concise
- Do not hallucinate
- Only respond to provided emails
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