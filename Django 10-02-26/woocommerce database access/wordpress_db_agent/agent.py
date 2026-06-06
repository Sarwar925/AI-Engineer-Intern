from __future__ import annotations

import os
import re
from difflib import SequenceMatcher
from typing import Any

from google.adk.agents import Agent
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEFAULT_MAX_ROWS = int(os.getenv("WP_DB_MAX_ROWS", "100"))
TABLE_PREFIX = os.getenv("WP_TABLE_PREFIX", "wp_")
PRODUCTS_TABLE_OVERRIDE = os.getenv("WP_PRODUCTS_TABLE", "").strip()
SEARCH_FALLBACK_LIMIT = int(os.getenv("WP_SEARCH_FALLBACK_LIMIT", "10"))
SEARCH_MATCH_THRESHOLD = float(os.getenv("WP_SEARCH_MATCH_THRESHOLD", "0.42"))
DEBUG_SEARCH = os.getenv("WP_DEBUG_SEARCH", "0").strip().lower() in {"1", "true", "yes", "on"}
READ_ONLY_PREFIXES = ("select", "show", "describe", "desc", "explain", "with")
STOP_WORDS = {
    "i",
    "want",
    "to",
    "buy",
    "show",
    "me",
    "the",
    "a",
    "an",
    "available",
    "product",
    "products",
    "for",
    "of",
    "in",
    "on",
    "please",
}
TOKEN_ALIASES = {
    "kamez": "kameez",
    "kameez": "kameez",
    "kamiz": "kameez",
    "kameezs": "kameez",
    "shalwar": "shalwar",
    "shalwaar": "shalwar",
    "shlwar": "shalwar",
    "shalvar": "shalwar",
}
PRODUCT_HINTS = {
    "kurta": 0.30,
    "shalwar": 0.30,
    "kameez": 0.30,
    "sherwani": 0.30,
    "waistcoat": 0.30,
    "shawl": 0.30,
    "pathani": 0.30,
    "pajama": 0.15,
    "coat": 0.10,
}
BLOCKED_PREFIXES = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "grant",
    "revoke",
    "replace",
    "rename",
    "call",
    "commit",
    "rollback",
    "set",
    "use",
)


def _db_config() -> dict[str, Any]:
    return {
        "host": os.environ["WP_DB_HOST"],
        "port": int(os.getenv("WP_DB_PORT", "3306")),
        "user": os.environ["WP_DB_USER"],
        "password": os.environ["WP_DB_PASSWORD"],
        "database": os.environ["WP_DB_NAME"],
        "connection_timeout": int(os.getenv("WP_DB_TIMEOUT", "10")),
    }


def _posts_table() -> str:
    return f"{TABLE_PREFIX}posts"


def _postmeta_table() -> str:
    return f"{TABLE_PREFIX}postmeta"


def _find_products_table(mysql_connector: Any) -> str | None:
    table_info = _discover_products_tables(mysql_connector)
    return table_info[0]["table_name"] if table_info else None


def _discover_products_tables(mysql_connector: Any) -> list[dict[str, Any]]:
    if PRODUCTS_TABLE_OVERRIDE:
        return [{"table_name": PRODUCTS_TABLE_OVERRIDE, "columns": "override", "score": 999}]

    conn = None
    cursor = None
    try:
        conn = mysql_connector.connect(**_db_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                table_name,
                GROUP_CONCAT(column_name ORDER BY column_name SEPARATOR ', ') AS columns,
                SUM(CASE WHEN column_name IN ('id', 'name', 'price', 'stock', 'description', 'category', 'short_description', 'product_name', 'product_price', 'product_stock') THEN 1 ELSE 0 END) AS score
            FROM information_schema.columns
            WHERE table_schema = %s
              AND column_name IN ('id', 'name', 'price', 'stock', 'description', 'category', 'short_description', 'product_name', 'product_price', 'product_stock')
            GROUP BY table_name
            HAVING score >= 3
            ORDER BY score DESC, table_name ASC
            """,
            (os.environ["WP_DB_NAME"],),
        )
        return cursor.fetchall() or []
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def _normalize_sql(sql: str) -> str:
    statement = sql.strip()
    if statement.endswith(";"):
        statement = statement[:-1].strip()
    return statement


def _normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def _search_tokens(value: str) -> list[str]:
    tokens = []
    for token in _normalize_text(value).split():
        if token in STOP_WORDS:
            continue
        tokens.append(TOKEN_ALIASES.get(token, token))
    return tokens


def _extract_best_query(query: str) -> str:
    tokens = _search_tokens(query)
    return " ".join(tokens)


def _similarity_score(query: str, candidate: str) -> float:
    query_norm = _normalize_text(query)
    candidate_norm = _normalize_text(candidate)
    query_tokens = _search_tokens(query)
    candidate_tokens = _search_tokens(candidate)

    if not query_norm or not candidate_norm:
        return 0.0

    direct = SequenceMatcher(None, query_norm, candidate_norm).ratio()
    direct_tokens = SequenceMatcher(None, " ".join(query_tokens), " ".join(candidate_tokens)).ratio()

    token_hits = 0.0
    for token in query_tokens:
        best = 0.0
        for candidate_token in candidate_tokens:
            best = max(best, SequenceMatcher(None, token, candidate_token).ratio())
        token_hits += best
    token_score = token_hits / max(len(query_tokens), 1)

    overlap = len(set(query_tokens) & set(candidate_tokens)) / max(len(set(query_tokens)), 1)
    contains_bonus = 0.25 if query_norm in candidate_norm else 0.0

    hint_bonus = sum(PRODUCT_HINTS.get(token, 0.0) for token in query_tokens if token in candidate_tokens)
    return max(direct, direct_tokens, token_score, overlap) + contains_bonus + hint_bonus


def _row_search_text(row: dict[str, Any]) -> str:
    parts = []
    for key in (
        "product_name",
        "name",
        "description",
        "short_description",
        "category",
        "categories",
        "product_category",
        "tags",
    ):
        value = row.get(key)
        if value not in (None, ""):
            parts.append(str(value))
    return " ".join(parts)


def _best_row_name(row: dict[str, Any]) -> str:
    for key in ("product_name", "name", "title"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _best_row_category(row: dict[str, Any]) -> str:
    for key in ("category", "categories", "product_category", "product_cat"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _stock_amount(row: dict[str, Any]) -> float:
    value = row.get("stock", 0)
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        text = str(value).strip().lower()
        if text in {"instock", "in_stock", "available", "yes", "true"}:
            return 1.0
        if text in {"outofstock", "out_of_stock", "no", "false"}:
            return 0.0
        digits = re.sub(r"[^0-9.]+", "", text)
        try:
            return float(digits) if digits else 0.0
        except ValueError:
            return 0.0


def _is_available(row: dict[str, Any]) -> bool:
    return _stock_amount(row) > 0


def _first_token(sql: str) -> str:
    match = re.match(r"^[\s]*(\w+)", sql, flags=re.IGNORECASE)
    return match.group(1).lower() if match else ""


def _is_read_only_sql(sql: str) -> bool:
    token = _first_token(sql)
    return token in READ_ONLY_PREFIXES and token not in BLOCKED_PREFIXES


def _apply_row_limit(sql: str, max_rows: int) -> str:
    token = _first_token(sql)
    if token not in ("select", "with"):
        return sql
    if re.search(r"\blimit\b", sql, flags=re.IGNORECASE):
        return sql
    return f"SELECT * FROM ({sql}) AS wp_query LIMIT {max_rows}"


def query_wordpress(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """Run a read-only SQL query against the WordPress database.

    Args:
        sql: A single read-only SQL statement, preferably a SELECT query.
        max_rows: Maximum number of rows to return for row-producing queries.
    """
    statement = _normalize_sql(sql)

    if not statement:
        return {"status": "error", "error": "SQL query is empty."}

    if not _is_read_only_sql(statement):
        return {
            "status": "error",
            "error": "Only read-only SQL is allowed. Use SELECT, SHOW, DESCRIBE, EXPLAIN, or WITH.",
        }

    statement = _apply_row_limit(statement, max_rows)

    try:
        import mysql.connector as mysql_connector
        from mysql.connector import Error
    except ModuleNotFoundError as exc:
        return {
            "status": "error",
            "error": (
                "mysql-connector-python is not installed in the active Python environment. "
                "Run `python -m pip install -r requirements.txt` in the same environment that starts ADK."
            ),
            "details": str(exc),
        }

    conn = None
    cursor = None
    try:
        conn = mysql_connector.connect(**_db_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute(statement)

        if cursor.description is not None:
            rows = cursor.fetchall()
            return {
                "status": "success",
                "row_count": len(rows),
                "rows": rows,
            }

        return {
            "status": "success",
            "row_count": cursor.rowcount,
            "rows": [],
        }
    except Error as exc:
        return {"status": "error", "error": str(exc)}
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def search_catalog(
    query: str = "",
    limit: int = 20,
    include_out_of_stock: bool = False,
    include_debug: bool = False,
) -> dict[str, Any]:
    """Search the product catalog using fuzzy matching and intent-aware ranking."""
    try:
        import mysql.connector as mysql_connector
        from mysql.connector import Error
    except ModuleNotFoundError as exc:
        return {
            "status": "error",
            "error": (
                "mysql-connector-python is not installed in the active Python environment. "
                "Run `python -m pip install -r requirements.txt` in the same environment that starts ADK."
            ),
            "details": str(exc),
        }

    table_candidates = _discover_products_tables(mysql_connector)
    products_table = table_candidates[0]["table_name"] if table_candidates else None
    if not products_table:
        return {
            "status": "error",
            "error": (
                "Could not find a products table in the database. "
                "Set WP_PRODUCTS_TABLE in .env to the table name that contains name, price, and stock columns."
            ),
        }

    sql = f"""
        SELECT
            *
        FROM `{products_table}`
        WHERE 1 = 1
        ORDER BY id DESC
    """

    conn = None
    cursor = None
    try:
        conn = mysql_connector.connect(**_db_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        all_rows = cursor.fetchall()
        rows = list(all_rows)

        if not include_out_of_stock:
            rows = [row for row in rows if _is_available(row)]

        query_text = query.strip()
        normalized_query = _extract_best_query(query_text)
        query_tokens = normalized_query.split() if normalized_query else []

        if query_text:
            scored_rows = []
            for row in rows:
                candidate_text = _row_search_text(row)
                score = _similarity_score(query_text, candidate_text)
                if score >= SEARCH_MATCH_THRESHOLD:
                    scored_rows.append((score, row))

            if not scored_rows and query_tokens:
                for row in rows:
                    candidate_tokens = set(_search_tokens(_row_search_text(row)))
                    overlap = len(set(query_tokens) & candidate_tokens)
                    if overlap > 0:
                        scored_rows.append((float(overlap) + 0.5, row))

            scored_rows.sort(
                key=lambda item: (
                    item[0],
                    float(item[1].get("stock") or 0),
                    int(item[1].get("id") or item[1].get("product_id") or 0),
                ),
                reverse=True,
            )
            rows = [row for score, row in scored_rows[:limit]]
        else:
            rows = rows[:limit]

        if query_text and not rows:
            fallback_rows = [row for row in all_rows if include_out_of_stock or _is_available(row)]
            rows = fallback_rows[:SEARCH_FALLBACK_LIMIT]

        results = []
        for row in rows:
            results.append(
                {
                    "id": row.get("id", row.get("product_id")),
                    "name": _best_row_name(row),
                    "price": row.get("price"),
                    "stock": row.get("stock"),
                    "is_available": _is_available(row),
                    "description": row.get("description"),
                    "category": _best_row_category(row),
                }
            )

        debug_payload = {}
        if include_debug or DEBUG_SEARCH:
            debug_payload = {
                "table_candidates": table_candidates[:5],
                "selected_table": products_table,
                "search_tokens": query_tokens,
                "threshold": SEARCH_MATCH_THRESHOLD,
                "matched_count": len(results),
            }

        return {
            "status": "success",
            "query": {
                "query": query,
                "limit": limit,
                "include_out_of_stock": include_out_of_stock,
                "products_table": products_table,
            },
            "row_count": len(results),
            "rows": results,
            "search_mode": "fuzzy" if query_text else "latest",
            "normalized_query": normalized_query,
            "debug": debug_payload,
        }
    except Error as exc:
        return {"status": "error", "error": str(exc)}
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


root_agent = Agent(
    name="wordpress_db_agent",
    model='openai/gpt-4o',
    description="A WordPress and WooCommerce database assistant that answers questions with safe, read-only SQL.",
    instruction=(
        "You are a helpful WordPress and WooCommerce database assistant. "
        "Always use the database tools when the user asks about products, orders, users, posts, categories, stock, prices, or counts. "
        "If the user wants to buy something or asks for available products, call search_catalog first with the full user request. "
        "Treat spelling mistakes, partial words, and loosely typed product names as search terms for fuzzy matching. "
        "If the user asks for a specific report or detail, use query_wordpress with a read-only query. "
        "Only run read-only queries. Never modify schema or data. "
        "When you answer, summarize the rows in plain language, mention how many items were found, and if the search was fuzzy, say that you matched the closest products."
    ),
    tools=[query_wordpress, search_catalog],
)
