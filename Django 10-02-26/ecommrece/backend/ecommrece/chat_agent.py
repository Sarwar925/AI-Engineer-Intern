import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import requests

from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google.adk.agents import LlmAgent
from google.adk.models import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv(Path(__file__).resolve().parent / ".env")
APP_NAME = "django_chat_app"
CHAT_MODEL = os.environ.get("CHAT_MODEL", "openai/gpt-4o")
API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


WOOCOMMERCE_API_URL = os.environ.get(
    "WOOCOMMERCE_API_URL"
)
WOOCOMMERCE_CONSUMER_KEY = os.environ.get(
    "WOOCOMMERCE_CONSUMER_KEY"
)
WOOCOMMERCE_CONSUMER_SECRET = os.environ.get(
    "WOOCOMMERCE_CONSUMER_SECRET"
)
WOOCOMMERCE_API_ROOT = ""


def _setting(name: str, fallback: str = "") -> str:
    try:
        value = getattr(settings, name, "")
    except ImproperlyConfigured:
        value = ""
    if value:
        return str(value).strip()
    return fallback.strip()


@dataclass(frozen=True)
class ChatUser:
    id: str
    email: str


def _slugify_email(email: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "_", email or "guest").strip("_").lower()
    digest = hashlib.md5((email or "guest").encode("utf-8")).hexdigest()[:8]
    return f"{base}_{digest}"[:150]


def get_or_create_chat_user(email: str) -> ChatUser:
    email = (email or "").strip().lower() or "guest@ecommrece.local"
    slug = _slugify_email(email)
    return ChatUser(id=slug, email=email)


def _content_to_text(content) -> str:
    if not content:
        return ""

    parts = getattr(content, "parts", None) or []
    chunks = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    return " ".join(chunks).strip()


def _woocommerce_api_root() -> str:
    global WOOCOMMERCE_API_ROOT
    if WOOCOMMERCE_API_ROOT:
        return WOOCOMMERCE_API_ROOT

    base_url = _setting("WOOCOMMERCE_API_URL", WOOCOMMERCE_API_URL).rstrip("/")
    if not base_url:
        return ""
    if base_url.endswith("/wc/v3"):
        WOOCOMMERCE_API_ROOT = base_url
        return WOOCOMMERCE_API_ROOT
    if base_url.endswith("/wp-json"):
        WOOCOMMERCE_API_ROOT = f"{base_url}/wc/v3"
        return WOOCOMMERCE_API_ROOT
    if "/wp-json/" in base_url:
        WOOCOMMERCE_API_ROOT = f"{base_url.rstrip('/')}/wc/v3"
        return WOOCOMMERCE_API_ROOT
    WOOCOMMERCE_API_ROOT = f"{base_url}/wp-json/wc/v3"
    return WOOCOMMERCE_API_ROOT


def _woocommerce_credentials_configured() -> bool:
    return bool(
        _woocommerce_api_root()
        and _setting("WOOCOMMERCE_CONSUMER_KEY", WOOCOMMERCE_CONSUMER_KEY)
        and _setting("WOOCOMMERCE_CONSUMER_SECRET", WOOCOMMERCE_CONSUMER_SECRET)
    )


def _woocommerce_credentials() -> tuple[str, str]:
    return (
        _setting("WOOCOMMERCE_CONSUMER_KEY", WOOCOMMERCE_CONSUMER_KEY),
        _setting("WOOCOMMERCE_CONSUMER_SECRET", WOOCOMMERCE_CONSUMER_SECRET),
    )


def _woocommerce_products_endpoint() -> str:
    api_root = _woocommerce_api_root()
    return f"{api_root}/products" if api_root else ""


def _woocommerce_request(endpoint: str, params: dict | None = None, use_basic_auth: bool = True):
    api_root = _woocommerce_api_root()
    if not api_root:
        raise RuntimeError("WOOCOMMERCE_API_URL is not configured.")

    endpoint_path = endpoint.lstrip("/")
    query_params = {key: value for key, value in dict(params or {}).items() if value not in ("", None)}
    consumer_key, consumer_secret = _woocommerce_credentials()
    candidates: list[tuple[str, dict[str, str], dict[str, str] | None]] = [
        (
            f"{api_root}/{endpoint_path}",
            {"Accept": "application/json"},
            {"consumer_key": consumer_key, "consumer_secret": consumer_secret}
            if api_root.startswith("http://")
            else None,
        )
    ]

    if "/wp-json/wc/v3" in api_root:
        root = api_root.split("/wp-json/wc/v3", 1)[0].rstrip("/")
        candidates.append(
            (
                f"{root}/index.php",
                {"Accept": "application/json"},
                {"rest_route": f"/wc/v3/{endpoint_path}"},
            )
        )

    last_error = ""

    def _attempt(url: str, headers: dict[str, str], extra_params: dict[str, str] | None, auth_mode: str) -> dict | list:
        request_params = dict(query_params)
        if extra_params:
            request_params.update(extra_params)

        with requests.Session() as session:
            session.trust_env = False
            if auth_mode == "query":
                request_params.update(
                    {
                        "consumer_key": consumer_key,
                        "consumer_secret": consumer_secret,
                    }
                )
                response = session.get(url, params=request_params, timeout=20, headers=headers)
            else:
                response = session.get(
                    url,
                    params=request_params,
                    auth=(consumer_key, consumer_secret),
                    timeout=20,
                    headers=headers,
                )

        if response.status_code in {401, 403}:
            body = response.text.strip()
            hint = ""
            if "woocommerce_rest_cannot_view" in body or "cannot list resources" in body.lower():
                hint = (
                    " The WooCommerce key/secret pair is valid but does not have permission to list products. "
                    "Regenerate the REST API key in WooCommerce with Read or Read/Write access for a user that can view products."
                )
            raise PermissionError(
                f"WooCommerce rejected the API credentials when calling {response.url}. "
                f"Status {response.status_code}. {body or 'No response body returned.'}{hint}"
            )

        response.raise_for_status()
        return response.json()

    for url, headers, extra_params in candidates:
        auth_order = ("query", "basic") if url.startswith("http://") else ("basic", "query")
        for auth_mode in auth_order:
            try:
                return _attempt(url, headers, extra_params, auth_mode)
            except PermissionError as exc:
                last_error = str(exc)
                continue
            except requests.Timeout as exc:
                raise ConnectionError(
                    f"WooCommerce API timed out when calling {url}. "
                    "Check that the WordPress site is running and that WOOCOMMERCE_API_URL is the actual store URL."
                ) from exc
            except requests.RequestException as exc:
                last_error = str(exc)
                continue

    if last_error:
        raise ConnectionError(last_error)

    raise ConnectionError(f"WooCommerce API could not be reached at {api_root}/{endpoint_path}.")


def debug_woocommerce_connection() -> dict[str, object]:
    api_root = _woocommerce_api_root()
    consumer_key, consumer_secret = _woocommerce_credentials()
    endpoint_path = "products"
    query_params = {
        "per_page": 1,
        "status": "publish",
        "_fields": "id,name,stock_status",
    }

    candidates: list[dict[str, object]] = [
        {
            "label": "direct_wc_v3",
            "url": f"{api_root}/{endpoint_path}" if api_root else "",
            "params": dict(query_params),
            "auth_mode": "query" if api_root.startswith("http://") else "basic",
        }
    ]

    if "/wp-json/wc/v3" in api_root:
        root = api_root.split("/wp-json/wc/v3", 1)[0].rstrip("/")
        candidates.append(
            {
                "label": "index_php_rest_route",
                "url": f"{root}/index.php",
                "params": {
                    **query_params,
                    "rest_route": f"/wc/v3/{endpoint_path}",
                },
                "auth_mode": "query",
            }
        )

    report: dict[str, object] = {
        "api_root": api_root,
        "configured": _woocommerce_credentials_configured(),
        "store_url": _setting("WOOCOMMERCE_API_URL", WOOCOMMERCE_API_URL),
        "tests": [],
    }

    for candidate in candidates:
        url = str(candidate["url"])
        auth_mode = str(candidate["auth_mode"])
        params = dict(candidate["params"])
        test_result: dict[str, object] = {
            "label": candidate["label"],
            "url": url,
            "auth_mode": auth_mode,
        }

        try:
            with requests.Session() as session:
                session.trust_env = False
                if auth_mode == "query":
                    params.update({"consumer_key": consumer_key, "consumer_secret": consumer_secret})
                    response = session.get(url, params=params, timeout=20, headers={"Accept": "application/json"})
                else:
                    response = session.get(
                        url,
                        params=params,
                        auth=(consumer_key, consumer_secret),
                        timeout=20,
                        headers={"Accept": "application/json"},
                    )

            test_result["status_code"] = response.status_code
            test_result["response_url"] = response.url
            test_result["content_type"] = response.headers.get("content-type", "")
            if response.ok:
                payload = response.json()
                test_result["result_type"] = type(payload).__name__
                test_result["item_count"] = len(payload) if isinstance(payload, list) else 1
                if isinstance(payload, list) and payload:
                    first = payload[0]
                    if isinstance(first, dict):
                        test_result["first_product"] = {
                            "id": first.get("id"),
                            "name": first.get("name"),
                            "stock_status": first.get("stock_status"),
                        }
            else:
                test_result["response_text"] = response.text[:500]
        except Exception as exc:
            test_result["error_type"] = type(exc).__name__
            test_result["error"] = str(exc)

        report["tests"].append(test_result)

    return report


def _clean_text(value: str) -> str:
    stripped = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", stripped).strip()


def _search_terms(query: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", (query or "").strip())
    if not cleaned:
        return []

    stopwords = {
        "what",
        "which",
        "show",
        "tell",
        "about",
        "please",
        "could",
        "would",
        "with",
        "from",
        "that",
        "this",
        "these",
        "those",
        "product",
        "products",
        "item",
        "items",
        "store",
        "shop",
        "available",
        "availability",
        "price",
        "prices",
        "stock",
    }

    tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9]+", cleaned)]
    terms = [token for token in tokens if len(token) > 2 and token not in stopwords]

    seen = set()
    ordered_terms = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            ordered_terms.append(term)
    return ordered_terms[:5]


def _looks_like_catalog_request(query: str) -> bool:
    text = (query or "").lower()
    keywords = {
        "available products",
        "available product",
        "show products",
        "show product",
        "list products",
        "list product",
        "all products",
        "catalog",
        "catalogue",
        "inventory",
        "what do you have",
        "what products do you have",
    }
    if any(phrase in text for phrase in keywords):
        return True

    tokens = set(re.findall(r"[a-z0-9]+", text))
    if tokens & {"available", "availability", "product", "products", "item", "items"} and not (
        tokens & {"price", "pricing", "color", "colors", "size", "sizes", "brand", "category"}
    ):
        return True

    # Catch common misspellings such as "availble products".
    typo_matches = {
        token
        for token in tokens
        if token in {"availble", "avialable", "availabe", "producs", "productes"}
    }
    return bool(typo_matches)


def _product_fields() -> str:
    return "id,name,price,regular_price,sale_price,short_description,description,permalink,stock_status,stock_quantity"


def _request_products(params: dict) -> list[dict]:
    response = _woocommerce_request("products", params=params)
    return response if isinstance(response, list) else []


def _fetch_products_with_fallbacks(param_sets: list[dict]) -> list[dict]:
    for params in param_sets:
        try:
            response = _request_products(params)
        except PermissionError as exc:
            return [exc]
        except ConnectionError as exc:
            return [exc]
        except (HTTPError, URLError, TimeoutError, RuntimeError):
            response = []

        if response:
            return response
    return []


def _format_product(product: dict) -> str:
    name = product.get("name") or "Unnamed product"
    price = product.get("price") or product.get("regular_price") or "N/A"
    stock_status = product.get("stock_status") or "unknown"
    stock_quantity = product.get("stock_quantity")
    permalink = product.get("permalink") or ""
    description = _clean_text(product.get("short_description") or product.get("description") or "")
    description = description[:180] + ("..." if len(description) > 180 else "")

    stock_bits = [f"stock: {stock_status}"]
    if stock_quantity is not None:
        stock_bits.append(f"qty: {stock_quantity}")

    pieces = [f"{name}", f"price: {price}", ", ".join(stock_bits)]
    if description:
        pieces.append(description)
    if permalink:
        pieces.append(permalink)
    return " | ".join(pieces)


def _debug_enabled() -> bool:
    return bool(getattr(settings, "DEBUG", False) or os.environ.get("WOOCOMMERCE_CHAT_DEBUG"))


def _fetch_relevant_products_sync(query: str) -> str:
    if not _woocommerce_credentials_configured():
        return (
            "WooCommerce is not configured. Set WOOCOMMERCE_API_URL, "
            "WOOCOMMERCE_CONSUMER_KEY, and WOOCOMMERCE_CONSUMER_SECRET."
        )

    search_terms = _search_terms(query)
    products: list[dict] = []
    wants_catalog = _looks_like_catalog_request(query)

    if wants_catalog:
        products = _fetch_products_with_fallbacks(
            [
                {
                    "per_page": 100,
                    "orderby": "date",
                    "order": "desc",
                    "status": "publish",
                    "_fields": _product_fields(),
                },
                {
                    "per_page": 100,
                    "orderby": "date",
                    "order": "desc",
                    "status": "any",
                    "_fields": _product_fields(),
                },
                {
                    "per_page": 100,
                    "orderby": "date",
                    "order": "desc",
                    "_fields": _product_fields(),
                },
            ]
        )
        if products and isinstance(products[0], PermissionError):
            return str(products[0])
        if products and isinstance(products[0], ConnectionError):
            return str(products[0])
    else:
        for term in search_terms:
            try:
                response = _request_products(
                    {
                        "search": term,
                        "per_page": 5,
                        "status": "publish",
                        "orderby": "relevance",
                        "_fields": _product_fields(),
                    }
                )
            except ConnectionError as exc:
                return str(exc)
            except PermissionError as exc:
                return str(exc)
            except (HTTPError, URLError, TimeoutError, RuntimeError):
                response = []

            for product in response:
                product_id = product.get("id")
                if product_id not in {item.get("id") for item in products}:
                    products.append(product)

            if len(products) >= 5:
                break

        if not products:
            try:
                fallback = _fetch_products_with_fallbacks(
                    [
                        {
                            "per_page": 20,
                            "orderby": "date",
                            "order": "desc",
                            "status": "publish",
                            "_fields": _product_fields(),
                        },
                        {
                            "per_page": 20,
                            "orderby": "date",
                            "order": "desc",
                            "status": "any",
                            "_fields": _product_fields(),
                        },
                    ]
                )
            except PermissionError as exc:
                return str(exc)
            except ConnectionError as exc:
                return str(exc)
            products = fallback

    if not products:
        if wants_catalog:
            return (
                "WooCommerce API connected, but it returned no products for the catalog request. "
                "Please verify that the store has published products and that the API user can read products."
            )
        return f"No WooCommerce products matched the query: {query or 'empty query'}."

    heading = "Available WooCommerce products:" if wants_catalog else "Relevant WooCommerce products:"
    lines = [f"User query: {query or 'empty query'}"]
    if _debug_enabled():
        lines.append(f"Debug: WooCommerce API connected. Found {len(products)} product(s).")
    lines.append(heading)
    lines.extend(f"- {_format_product(product)}" for product in products[:5])
    return "\n".join(lines)


def _spell_correction_hint(query: str) -> str:
    # Keep this lightweight and deterministic; the model can still interpret intent.
    normalized = re.sub(r"\s+", " ", query or "").strip()
    return normalized


def _build_live_instruction(user: ChatUser):
    async def _instruction(ctx) -> str:
        query = _content_to_text(ctx.user_content)
        corrected_query = _spell_correction_hint(query)
        product_summary = await sync_to_async(_fetch_relevant_products_sync)(corrected_query)
        return f"""
You are a helpful assistant for an e-commerce storefront.
Answer only in English.
Use the WooCommerce product context below on every reply.
Never invent product names, prices, stock, or availability.
If the context does not include a matching product, say that clearly and briefly.
If the user asks a follow-up about a product, keep the answer grounded in the WooCommerce data shown below.

User query: {corrected_query}

{product_summary}
""".strip()

    return _instruction


chat_model_engine = LiteLlm(model=CHAT_MODEL, api_key=API_KEY)
session_service = InMemorySessionService()


def get_agent(user: ChatUser):
    return LlmAgent(
        model=chat_model_engine,
        name="root_agent",
        instruction=_build_live_instruction(user),
        tools=[],
    )


async def _get_session(user: ChatUser):
    session_id = f"chat-{user.id}"
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=str(user.id),
        session_id=session_id,
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=str(user.id),
            session_id=session_id,
            state={"email": user.email},
        )
    return session


def _fallback_response(message: str) -> str:
    product_summary = _fetch_relevant_products_sync(message)
    return (
        "I could not reach the AI model, but here is what I found from WooCommerce:\n"
        f"{product_summary}"
    )


async def run_chat_agent_async(user: ChatUser, message: str) -> str:
    if _looks_like_catalog_request(message):
        return _fetch_relevant_products_sync(message)

    if not API_KEY:
        return _fallback_response(message)

    agent = get_agent(user)
    session = await _get_session(user)
    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )

    user_message = types.Content(role="user", parts=[types.Part(text=message)])
    final_text = ""

    async for event in runner.run_async(
        user_id=str(user.id),
        session_id=session.id,
        new_message=user_message,
    ):
        text = _content_to_text(getattr(event, "content", None))
        if text:
            final_text = text

    if final_text:
        return final_text

    return _fallback_response(message)


def run_chat_agent(user: ChatUser, message: str) -> str:
    return asyncio.run(run_chat_agent_async(user, message))
