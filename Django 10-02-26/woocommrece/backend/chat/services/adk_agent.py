import hashlib
import os
import re
from typing import Any

import requests
import dotenv
from django.conf import settings

from .woocommerce import is_product_query, lookup_store_facts

# -------------------------------------------- #
# ------ Environment and agent defaults ------ #
# -------------------------------------------- #
dotenv.load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
APP_NAME = "woo_chat_agent"
USER_ID_PREFIX = "woo_user"
_AGENT: Any | None = None
_RUNNER: Any | None = None

# -------------------------------------------- #
# Session identity helpers and text processing #
# -------------------------------------------- #
def _slugify_email(email: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "_", email or "guest").strip("_").lower()
    digest = hashlib.md5((email or "guest").encode("utf-8")).hexdigest()[:8]
    return f"{base}_{digest}"[:150]

# -------------------------------------------- #
# Small text cleanup helpers and store summary #
# -------------------------------------------- #
def _spell_correction_hint(query: str) -> str:
    return re.sub(r"\s+", " ", query or "").strip()

# ------------------------------------------------- #
# -Local store summary used for fallback responses- #
# ------------------------------------------------- #
def _store_summary_sync(query: str) -> str:
    facts = lookup_store_facts(query)
    products = facts.get("products", []) or []
    source = facts.get("source", "wordpress_database")
    if not products:
        return f"Store source: {source}. Store products: no matching products found."

    details = "; ".join(
        f"{index}. {product.get('name', 'Unnamed')} | price {product.get('price', '')} | stock {product.get('status', '')} | sku {product.get('sku', '')}"
        for index, product in enumerate(products, start=1)
    )
    return f"Store source: {source}. Store products: {len(products)} matching product(s). Details: {details}."

# --------------------------------------------- #
# ---Extract plain text from model responses--- #
# --------------------------------------------- #
def _extract_message_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        chunks = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    chunks.append(str(text))
            elif item:
                chunks.append(str(item))
        return " ".join(chunks).strip()
    if isinstance(value, dict):
        if "text" in value:
            return str(value["text"]).strip()
        if "content" in value:
            return _extract_message_text(value["content"])
    if hasattr(value, "parts"):
        parts = []
        for part in getattr(value, "parts", []) or []:
            text = getattr(part, "text", None)
            if text:
                parts.append(str(text))
        return " ".join(parts).strip()
    return str(value).strip()

# -------------------------------------------------------- #
# -Simple fallback reply when AI services are unavailable- #
# -------------------------------------------------------- #
def _fallback_reply(message: str) -> str:
    if is_product_query(message):
        return _store_summary_sync(message)

    return (
        "I can help with general questions and WooCommerce product lookups. "
        "Ask me about a product, price, stock, or availability."
    )

# --------------------------------------------- #
# ----Build the OpenAI conversation payload---- #
# --------------------------------------------- #
def _build_openai_messages(user_email: str, message: str) -> list[dict[str, str]]:
    cleaned_message = _spell_correction_hint(message)
    if is_product_query(cleaned_message):
        store_summary = _store_summary_sync(cleaned_message)
        system_prompt = (
            "You are a helpful WooCommerce assistant. "
            "Answer in English using only the provided store context. "
            "Do not invent facts."
        )
        user_prompt = (
            f"User query: {cleaned_message}\n"
            f"Customer email: {user_email or 'guest'}\n"
            f"Store context: {store_summary}"
        )
    else:
        system_prompt = (
            "You are a helpful general-purpose assistant for a WooCommerce website. "
            "Answer in English with a clear, natural, and concise response."
        )
        user_prompt = cleaned_message

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

# --------------------------------------------- #
# ---------OpenAI chat completion path--------- #
# --------------------------------------------- #
def _call_openai_chat(user_email: str, message: str) -> str:
    if not OPENAI_API_KEY:
        return ""

    payload = {
        "model": OPENAI_MODEL,
        "messages": _build_openai_messages(user_email, message),
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    with requests.Session() as session:
        session.trust_env = False
        response = session.post(
            f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=45,
        )

    response.raise_for_status()
    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        return ""

    message_obj = (choices[0] or {}).get("message") or {}
    return _extract_message_text(message_obj.get("content"))

# -------------------------------------------- #
# ------ADK tool wrapper for store facts------ #
# -------------------------------------------- #
def _lookup_store_facts_tool(query: str) -> dict[str, Any]:
    return lookup_store_facts(query)

# -------------------------------------------- #
# -------Google ADK agent construction-------- #
# -------------------------------------------- #
def _build_agent() -> Any:
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool

    model_name = getattr(settings, "ADK_MODEL", "") or "openai/gpt-4o"
    instruction = """
You are a helpful WooCommerce assistant.
Answer in English.

If the user asks about products, prices, stock, availability, SKU, categories, or store content:
- Use the lookup_store_facts tool.
- Be tolerant of spelling mistakes and messy input.
- Base your answer only on the returned store data.
- Never invent product facts.

If the tool returns no matching products:
- Say that you could not find a confident match.
- Ask the user to rephrase or share a clearer product name.

If the user is making general conversation:
- Answer naturally and do not mention store data unless it is relevant.
""".strip()

    return LlmAgent(
        name=APP_NAME,
        model=model_name,
        instruction=instruction,
        tools=[FunctionTool(_lookup_store_facts_tool)],
    )

# -------------------------------------------- #
# ------------Cached agent instance----------- #
# -------------------------------------------- #

def _get_agent() -> Any:
    global _AGENT
    if _AGENT is None:
        _AGENT = _build_agent()
    return _AGENT

# -------------------------------------------- #
# -----------Cached runner instance----------- #
# -------------------------------------------- #

def _get_runner() -> Any:
    from google.adk.runners import InMemoryRunner

    global _RUNNER
    if _RUNNER is None:
        _RUNNER = InMemoryRunner(agent=_get_agent(), app_name=APP_NAME)
    return _RUNNER

# -------------------------------------------- #
# ---------Per-user session identity---------- #
# -------------------------------------------- #
def _session_identity(email: str) -> tuple[str, str]:
    user_id = f"{USER_ID_PREFIX}_{_slugify_email(email)}"
    session_id = f"{APP_NAME}_{_slugify_email(email)}"
    return user_id, session_id

# --------------------------------------------- #
# -----Main chat orchestration entry point----- #
# --------------------------------------------- #
def run_chat_agent(user_email: str, message: str) -> str:
    cleaned_message = _spell_correction_hint(message)
    if not cleaned_message:
        return ""

    if OPENAI_API_KEY:
        try:
            reply = _call_openai_chat(user_email, cleaned_message)
            if reply.strip():
                return reply.strip()
        except Exception:
            pass

    if not getattr(settings, "GOOGLE_API_KEY", ""):
        return _fallback_reply(cleaned_message)

    try:
        runner = _get_runner()
        user_id, session_id = _session_identity(user_email)
        from google.genai import types

        new_message = types.Content(role="user", parts=[types.Part(text=cleaned_message)])
        final_reply = ""

        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
        ):
            if getattr(event, "is_final_response", lambda: False)():
                final_reply = _extract_message_text(getattr(event, "content", None)) or final_reply
            else:
                event_text = _extract_message_text(getattr(event, "content", None))
                if event_text:
                    final_reply = event_text

        if final_reply.strip():
            return final_reply.strip()
    except Exception:
        return _fallback_reply(cleaned_message)

    return _fallback_reply(cleaned_message)

# -------------------------------------------- #
# ----Public reply helper used by the view---- #
# -------------------------------------------- #
def generate_reply(message: str, email: str = "") -> str:
    return run_chat_agent(email, message)

