import base64
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any
import re

import requests
from django.conf import settings
from django.db import DatabaseError, connection

# ----------------------------------------------- #
# ----Store query keywords and matching rules---- #
# ----------------------------------------------- #
PRODUCT_META_KEYS = ("_price", "_regular_price", "_stock_status", "_stock", "_sku")
GREETING_PHRASES = (
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "what's up",
    "whats up",
    "thank you",
    "thanks",
)
PRODUCT_TERMS = (
    "product",
    "products",
    "item",
    "items",
    "price",
    "pricing",
    "cost",
    "stock",
    "available",
    "availability",
    "buy",
    "purchase",
    "order",
    "category",
    "catalog",
    "store",
    "shop",
    "woocommerce",
    "sku",
)
PRODUCT_PHRASES = (
    "show me",
    "find me",
    "find",
    "search for",
    "tell me about",
    "price of",
    "cost of",
    "in stock",
    "stock of",
    "available",
    "availability",
    "product details",
    "product info",
)

# ----------------------------------------------- #
# --------WooCommerce API client wrapper--------- #
# ----------------------------------------------- #
@dataclass
class WooCommerceClient:
    base_url: str
    consumer_key: str
    consumer_secret: str

    def _headers(self) -> dict[str, str]:
        token = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode("utf-8")
        ).decode("utf-8")
        return {"Authorization": f"Basic {token}"}

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        with requests.Session() as session:
            session.trust_env = False
            response = session.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=20,
            )
        response.raise_for_status()
        return response.json()


# ----------------------------------------------- #
# ------Environment-backed API client setup------ #
# ----------------------------------------------- #
def get_client() -> WooCommerceClient | None:
    if not (
        settings.WOOCOMMERCE_API_URL
        and settings.WOOCOMMERCE_CONSUMER_KEY
        and settings.WOOCOMMERCE_CONSUMER_SECRET
    ):
        return None

    return WooCommerceClient(
        base_url=settings.WOOCOMMERCE_API_URL,
        consumer_key=settings.WOOCOMMERCE_CONSUMER_KEY,
        consumer_secret=settings.WOOCOMMERCE_CONSUMER_SECRET,
    )

# ----------------------------------------------- #
# ----Text cleanup and fuzzy matching helpers---- #
# ----------------------------------------------- #
def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _tokenize(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", _normalize_text(value))


def _similarity(left: str, right: str) -> float:
    left_normalized = _normalize_text(left)
    right_normalized = _normalize_text(right)
    if not left_normalized or not right_normalized:
        return 0.0
    return SequenceMatcher(None, left_normalized, right_normalized).ratio()


def _contains_fuzzy_term(query: str, terms: tuple[str, ...], threshold: float = 0.82) -> bool:
    tokens = _tokenize(query)
    if not tokens:
        return False

    for token in tokens:
        if len(token) < 3:
            continue
        for term in terms:
            if token == term:
                return True
            if len(term) < 4:
                continue
            if _similarity(token, term) >= threshold:
                return True
    return False


def _is_broad_product_request(query: str) -> bool:
    normalized = _normalize_text(query)
    if not normalized:
        return False

    broad_phrases = (
        "available products",
        "products available",
        "list products",
        "show products",
        "all products",
        "product list",
        "products in database",
        "products available in database",
        "what products",
        "show me products",
    )
    return any(phrase in normalized for phrase in broad_phrases)


def is_product_query(query: str) -> bool:
    normalized = _normalize_text(query)
    if not normalized:
        return False

    if normalized in GREETING_PHRASES or any(
        normalized.startswith(f"{phrase} ") for phrase in GREETING_PHRASES
    ):
        return False

    if _is_broad_product_request(normalized):
        return True

    if any(phrase in normalized for phrase in PRODUCT_PHRASES):
        return True

    if any(re.search(rf"\b{re.escape(term)}\b", normalized) for term in PRODUCT_TERMS):
        return True

    return _contains_fuzzy_term(normalized, PRODUCT_TERMS)


# ----------------------------------------------- #
# -------Database table discovery helpers-------- #
# ----------------------------------------------- #
def _find_table_name(suffix: str) -> str | None:
    try:
        table_names = connection.introspection.table_names()
    except DatabaseError:
        return None

    exact = [name for name in table_names if name == suffix]
    if exact:
        return exact[0]

    preferred = [name for name in table_names if name.endswith(f"_{suffix}")]
    if preferred:
        return sorted(preferred, key=len)[0]

    fallback = [name for name in table_names if name.endswith(suffix)]
    if fallback:
        return sorted(fallback, key=len)[0]

    return None

# ---------------------------------------------------- #
# --Detailed product search against WordPress tables-- #
# ---------------------------------------------------- #
def _fetch_database_products(query: str, limit: int = 600) -> list[dict[str, Any]]:
    normalized = _normalize_text(query)
    if not normalized:
        return []

    posts_table = _find_table_name("posts")
    postmeta_table = _find_table_name("postmeta")
    if not posts_table or not postmeta_table:
        return []

    sql = f"""
        SELECT
            p.ID,
            p.post_title,
            p.post_name,
            p.post_excerpt,
            p.post_content,
            MAX(CASE WHEN pm.meta_key = '_price' THEN pm.meta_value END) AS price,
            MAX(CASE WHEN pm.meta_key = '_regular_price' THEN pm.meta_value END) AS regular_price,
            MAX(CASE WHEN pm.meta_key = '_stock_status' THEN pm.meta_value END) AS stock_status,
            MAX(CASE WHEN pm.meta_key = '_stock' THEN pm.meta_value END) AS stock,
            MAX(CASE WHEN pm.meta_key = '_sku' THEN pm.meta_value END) AS sku
        FROM `{posts_table}` p
        LEFT JOIN `{postmeta_table}` pm
            ON pm.post_id = p.ID
           AND pm.meta_key IN ('_price', '_regular_price', '_stock_status', '_stock', '_sku')
        WHERE p.post_type = 'product'
          AND p.post_status IN ('publish', 'private')
        GROUP BY
            p.ID,
            p.post_title,
            p.post_name,
            p.post_excerpt,
            p.post_content
        ORDER BY p.ID DESC
        LIMIT %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [limit])
            columns = [column[0] for column in cursor.description or []]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except DatabaseError:
        return []

    candidates: list[dict[str, Any]] = []
    query_tokens = set(_tokenize(normalized))
    for row in rows:
        name = str(row.get("post_title") or "").strip()
        excerpt = str(row.get("post_excerpt") or "").strip()
        content = str(row.get("post_content") or "").strip()
        sku = str(row.get("sku") or "").strip()
        searchable = " ".join(part for part in [name, sku, excerpt, content] if part)

        title_score = _similarity(normalized, name)
        searchable_score = _similarity(normalized, searchable)
        token_score = 0.0
        if query_tokens:
            product_tokens = set(_tokenize(searchable))
            exact_overlap = query_tokens & product_tokens
            fuzzy_hits = 0
            for token in query_tokens:
                best_similarity = 0.0
                for product_token in product_tokens:
                    best_similarity = max(best_similarity, _similarity(token, product_token))
                if best_similarity >= 0.82:
                    fuzzy_hits += 1
            token_score = max(
                len(exact_overlap) / len(query_tokens),
                fuzzy_hits / len(query_tokens),
            )

        exact_bonus = 0.0
        if normalized in _normalize_text(searchable):
            exact_bonus += 0.25
        if sku and sku.lower() in normalized:
            exact_bonus += 0.15
        if normalized in _normalize_text(sku):
            exact_bonus += 0.15

        score = (
            (title_score * 0.45)
            + (searchable_score * 0.25)
            + (token_score * 0.25)
            + exact_bonus
        )

        candidates.append(
            {
                "id": row.get("ID"),
                "name": name or "Unnamed product",
                "price": row.get("price"),
                "regular_price": row.get("regular_price"),
                "status": row.get("stock_status") or "publish",
                "stock": row.get("stock"),
                "sku": sku,
                "source": "wordpress_database",
                "score": score,
            }
        )

    ranked = sorted(candidates, key=lambda item: item["score"], reverse=True)
    if not ranked or ranked[0]["score"] < 0.18:
        return []

    top = [item for item in ranked if item["score"] >= 0.18][:8]
    return top


# ------------------------------------------------------- #
# ---Broad product catalog fetch from WordPress tables--- #
# ------------------------------------------------------- #
def _fetch_database_catalog(limit: int = 8) -> list[dict[str, Any]]:
    posts_table = _find_table_name("posts")
    postmeta_table = _find_table_name("postmeta")
    if not posts_table or not postmeta_table:
        return []

    sql = f"""
        SELECT
            p.ID,
            p.post_title,
            p.post_name,
            p.post_excerpt,
            p.post_content,
            MAX(CASE WHEN pm.meta_key = '_price' THEN pm.meta_value END) AS price,
            MAX(CASE WHEN pm.meta_key = '_regular_price' THEN pm.meta_value END) AS regular_price,
            MAX(CASE WHEN pm.meta_key = '_stock_status' THEN pm.meta_value END) AS stock_status,
            MAX(CASE WHEN pm.meta_key = '_stock' THEN pm.meta_value END) AS stock,
            MAX(CASE WHEN pm.meta_key = '_sku' THEN pm.meta_value END) AS sku
        FROM `{posts_table}` p
        LEFT JOIN `{postmeta_table}` pm
            ON pm.post_id = p.ID
           AND pm.meta_key IN ('_price', '_regular_price', '_stock_status', '_stock', '_sku')
        WHERE p.post_type = 'product'
          AND p.post_status IN ('publish', 'private')
        GROUP BY
            p.ID,
            p.post_title,
            p.post_name,
            p.post_excerpt,
            p.post_content
        ORDER BY p.ID DESC
        LIMIT %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [limit])
            columns = [column[0] for column in cursor.description or []]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except DatabaseError:
        return []

    products: list[dict[str, Any]] = []
    for row in rows:
        products.append(
            {
                "id": row.get("ID"),
                "name": str(row.get("post_title") or "").strip() or "Unnamed product",
                "price": row.get("price"),
                "regular_price": row.get("regular_price"),
                "status": row.get("stock_status") or "publish",
                "stock": row.get("stock"),
                "sku": str(row.get("sku") or "").strip(),
                "source": "wordpress_database",
                "score": 1.0,
            }
        )
    return products

# ----------------------------------------------- #
# ----------Custom product table search---------- #
# ----------------------------------------------- #
def _fetch_custom_products(query: str, limit: int = 600) -> list[dict[str, Any]]:
    normalized = _normalize_text(query)
    if not normalized:
        return []

    table_name = _find_table_name("custom_products")
    if not table_name:
        return []

    sql = f"""
        SELECT
            id,
            product_id,
            name,
            price,
            stock
        FROM `{table_name}`
        ORDER BY id DESC
        LIMIT %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [limit])
            columns = [column[0] for column in cursor.description or []]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except DatabaseError:
        return []

    candidates: list[dict[str, Any]] = []
    query_tokens = set(_tokenize(normalized))
    for row in rows:
        name = str(row.get("name") or "").strip()
        product_id = str(row.get("product_id") or "").strip()
        searchable = " ".join(part for part in [name, product_id] if part)

        title_score = _similarity(normalized, name)
        searchable_score = _similarity(normalized, searchable)
        token_score = 0.0
        if query_tokens:
            product_tokens = set(_tokenize(searchable))
            exact_overlap = query_tokens & product_tokens
            fuzzy_hits = 0
            for token in query_tokens:
                best_similarity = 0.0
                for product_token in product_tokens:
                    best_similarity = max(best_similarity, _similarity(token, product_token))
                if best_similarity >= 0.82:
                    fuzzy_hits += 1
            token_score = max(
                len(exact_overlap) / len(query_tokens),
                fuzzy_hits / len(query_tokens),
            )

        exact_bonus = 0.0
        if normalized in _normalize_text(searchable):
            exact_bonus += 0.25

        score = (
            (title_score * 0.5)
            + (searchable_score * 0.2)
            + (token_score * 0.3)
            + exact_bonus
        )

        candidates.append(
            {
                "id": row.get("id"),
                "name": name or "Unnamed product",
                "price": row.get("price"),
                "status": "publish",
                "stock": row.get("stock"),
                "sku": product_id,
                "source": "custom_products_table",
                "score": score,
            }
        )

    ranked = sorted(candidates, key=lambda item: item["score"], reverse=True)
    if not ranked or ranked[0]["score"] < 0.18:
        return []

    return [item for item in ranked if item["score"] >= 0.18][:8]

# --------------------------------------------------------- #
# ----Broad product catalog fetch from the custom table---- #
# --------------------------------------------------------- #
def _fetch_custom_catalog(limit: int = 8) -> list[dict[str, Any]]:
    table_name = _find_table_name("custom_products")
    if not table_name:
        return []

    sql = f"""
        SELECT
            id,
            product_id,
            name,
            price,
            stock
        FROM `{table_name}`
        ORDER BY id DESC
        LIMIT %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [limit])
            columns = [column[0] for column in cursor.description or []]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except DatabaseError:
        return []

    products: list[dict[str, Any]] = []
    for row in rows:
        products.append(
            {
                "id": row.get("id"),
                "name": str(row.get("name") or "").strip() or "Unnamed product",
                "price": row.get("price"),
                "status": "publish",
                "stock": row.get("stock"),
                "sku": str(row.get("product_id") or "").strip(),
                "source": "custom_products_table",
                "score": 1.0,
            }
        )
    return products

# ----------------------------------------------------- #
# --------WooCommerce REST API fallback search--------- #
# ----------------------------------------------------- #
def _search_products_from_api(query: str) -> list[dict[str, Any]]:
    client = get_client()
    if client is None or not query.strip():
        return []

    params: dict[str, Any] = {"per_page": 100}
    if _is_broad_product_request(query):
        params["status"] = "publish"
    else:
        params["search"] = query

    try:
        data = client.get("products", params=params)
    except requests.RequestException:
        return []

    results: list[dict[str, Any]] = []
    for item in data:
        results.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "price": item.get("price"),
                "status": item.get("status"),
                "sku": item.get("sku"),
                "permalink": item.get("permalink"),
                "source": "woocommerce_api",
                "score": 1.0,
            }
        )
    return results

# ----------------------------------------------------- #
# -----------Main product lookup entry point----------- #
# ----------------------------------------------------- #
def search_products(query: str) -> list[dict[str, Any]]:
    """Search store products using the WordPress database first."""
    if not query.strip():
        return []

    if _is_broad_product_request(query):
        catalog = [*_fetch_database_catalog(), *_fetch_custom_catalog()]
        if catalog:
            return sorted(
                catalog,
                key=lambda item: int(item.get("id") or 0),
                reverse=True,
            )[:8]
        return _search_products_from_api(query)

    products = _fetch_database_products(query)
    custom_products = _fetch_custom_products(query)
    merged = sorted(
        [*products, *custom_products],
        key=lambda item: item["score"],
        reverse=True,
    )
    if merged:
        return merged[:8]

    return _search_products_from_api(query)

# ------------------------------------------------------ #
# ----Store facts wrapper used by chat and the agent---- #
# ------------------------------------------------------ #
def lookup_store_facts(query: str) -> dict[str, Any]:
    """Return WooCommerce facts for the current chat query."""
    products = search_products(query)
    return {
        "products": products,
        "source": products[0]["source"] if products else "wordpress_database",
        "store_url": settings.WOOCOMMERCE_API_URL,
    }
