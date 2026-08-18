# import os
# import imaplib
# import smtplib
# import email
# import time
# import logging
# from email.mime.text import MIMEText
# from dotenv import load_dotenv

# from google.adk.agents import Agent
# from openai import OpenAI

# # ======================
# # CONFIG
# # ======================
# load_dotenv()

# EMAIL = os.getenv("EMAIL")
# APP_PASSWORD = os.getenv("APP_PASSWORD")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# CHECK_INTERVAL = 15

# client = OpenAI(api_key=OPENAI_API_KEY)

# logging.basicConfig(level=logging.INFO)

# # Memory store (replace with DB in real prod)
# PROCESSED = set()

# # ======================
# # PARSE EMAIL
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
# # TOOL: READ EMAILS
# # ======================
# def read_emails() -> list:
#     """Fetch unread emails from all users"""
#     results = []

#     try:
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         mail.login(EMAIL, APP_PASSWORD)
#         mail.select("inbox")

#         status, messages = mail.search(None, '(UNSEEN)')
#         email_ids = messages[0].split()

#         for e_id in email_ids:
#             if e_id in PROCESSED:
#                 continue

#             _, msg_data = mail.fetch(e_id, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             from_email = email.utils.parseaddr(msg.get("From"))[1]
#             subject = msg.get("Subject", "")
#             message_id = msg.get("Message-ID", "")
#             in_reply_to = msg.get("In-Reply-To", "")

#             body = extract_body(msg)

#             results.append({
#                 "id": e_id.decode(),
#                 "from": from_email,
#                 "subject": subject,
#                 "body": body,
#                 "message_id": message_id,
#                 "thread_id": in_reply_to or message_id
#             })

#             PROCESSED.add(e_id)

#         mail.logout()

#     except Exception as e:
#         logging.error(f"Read error: {e}")

#     return results

# # ======================
# # TOOL: SEND EMAIL (THREAD)
# # ======================
# def send_email(to: str, subject: str, reply_text: str, thread_id: str) -> str:
#     """Send threaded reply"""
#     try:
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(EMAIL, APP_PASSWORD)

#         msg = MIMEText(reply_text)
#         msg["From"] = EMAIL
#         msg["To"] = to
#         msg["Subject"] = f"Re: {subject}"
#         msg["In-Reply-To"] = thread_id
#         msg["References"] = thread_id

#         server.sendmail(EMAIL, to, msg.as_string())
#         server.quit()

#         return "sent"

#     except Exception as e:
#         logging.error(f"Send error: {e}")
#         return "failed"

# # ======================
# # CLASSIFY EMAIL
# # ======================
# def classify_email(text):
#     prompt = f"""
#     Classify this email into one category:
#     - support
#     - sales
#     - spam

#     Email:
#     {text}

#     Only return category name.
#     """

#     res = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return res.choices[0].message.content.strip().lower()

# # ======================
# # GENERATE REPLY
# # ======================
# def generate_reply(text, category):
#     prompt = f"""
#     You are an AI email assistant.

#     Category: {category}

#     Write a professional reply.

#     Email:
#     {text}
#     """

#     res = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return res.choices[0].message.content

# # ======================
# # AGENT
# # ======================
# agent = Agent(
#     name="Email_Agent",
#     instruction="Process emails, classify, and reply professionally.",
#     tools=[read_emails, send_email],
# )

# # ======================
# # PROCESS LOOP
# # ======================
# def process():
#     emails = read_emails()

#     if not emails:
#         logging.info("No emails")
#         return

#     for e in emails:
#         logging.info(f"Processing from {e['from']}")

#         category = classify_email(e["body"])

#         if category == "spam":
#             logging.info("Spam detected, skipping")
#             continue

#         reply = generate_reply(e["body"], category)

#         send_email(e["from"], e["subject"], reply, e["thread_id"])

#         logging.info(f"Replied to {e['from']} [{category}]")

# # ======================
# # WORKER
# # ======================
# def run():
#     logging.info("🚀 SaaS-Level Email Agent Running...")

#     while True:
#         try:
#             process()
#         except Exception as e:
#             logging.error(f"Error: {e}")

#         time.sleep(CHECK_INTERVAL)

# # ======================
# # ENTRY
# # ======================
# if __name__ == "__main__":
#     run()









import os
import imaplib
import smtplib
import email
import time
import logging
import warnings
from email.mime.text import MIMEText
from dotenv import load_dotenv
from openai import OpenAI

# ======================
# FIX: Silence warnings (Pydantic / ADK noise)
# ======================
# warnings.filterwarnings("ignore", category=UserWarning)

# ======================
# CONFIG
# ======================
load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CHECK_INTERVAL = 15

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

PROCESSED = set()

# ======================
# EMAIL PARSER
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
    return ""

# ======================
# READ EMAILS
# ======================
def read_emails():
    results = []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox")

        # FIX: use ALL instead of UNSEEN if needed
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        for e_id in email_ids:
            eid = e_id.decode()

            if eid in PROCESSED:
                continue

            _, msg_data = mail.fetch(e_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            from_email = email.utils.parseaddr(msg.get("From"))[1]
            subject = msg.get("Subject", "")
            message_id = msg.get("Message-ID", "")
            in_reply_to = msg.get("In-Reply-To", "")

            body = extract_body(msg)

            results.append({
                "id": eid,
                "from": from_email,
                "subject": subject,
                "body": body,
                "message_id": message_id,
                "thread_id": in_reply_to or message_id
            })

            PROCESSED.add(eid)

        mail.logout()

    except Exception as e:
        logging.error(f"Read error: {e}")

    return results

# ======================
# SEND EMAIL
# ======================
def send_email(to, subject, reply_text, thread_id):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)

        msg = MIMEText(reply_text)
        msg["From"] = EMAIL
        msg["To"] = to
        msg["Subject"] = f"Re: {subject}"
        msg["In-Reply-To"] = thread_id
        msg["References"] = thread_id

        server.sendmail(EMAIL, to, msg.as_string())
        server.quit()

        return "sent"

    except Exception as e:
        logging.error(f"Send error: {e}")
        return "failed"

# ======================
# CLASSIFY EMAIL (FIXED)
# ======================
def classify_email(text):
    prompt = f"""
You are an email classifier.

Return ONLY one word:
support, sales, or spam

Rules:
- lowercase only
- no punctuation
- no explanation

Email:
{text}
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content.strip().lower().replace(".", "")

# ======================
# GENERATE REPLY
# ======================
def generate_reply(text, category):
    prompt = f"""
You are a professional AI email assistant.

Category: {category}

Write a short, clear, professional reply.

Email:
{text}
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return res.choices[0].message.content.strip()

# ======================
# PROCESS EMAILS
# ======================
def process():
    emails = read_emails()

    if not emails:
        logging.info("No emails")
        return

    for e in emails:
        logging.info(f"Processing from {e['from']}")

        category = classify_email(e["body"])

        logging.info(f"Category: {category}")

        if category == "spam":
            logging.info("Spam detected, skipping")
            continue

        reply = generate_reply(e["body"], category)

        send_email(
            e["from"],
            e["subject"],
            reply,
            e["thread_id"]
        )

        logging.info(f"Replied to {e['from']}")

# ======================
# MAIN LOOP
# ======================
def run():
    logging.info("🚀 Email Agent Running...")

    while True:
        try:
            process()
        except Exception as e:
            logging.error(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)

# ======================
# START
# ======================
if __name__ == "__main__":
    run()