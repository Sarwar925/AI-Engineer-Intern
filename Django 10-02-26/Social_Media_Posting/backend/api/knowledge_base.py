import io
import os
import re
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager

from django.conf import settings
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import dotenv
dotenv.load_dotenv()
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "ghulamsarwarwork")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "AWS us-east-1")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "Langchain-1")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
EMBEDDING_MODEL = os.getenv("CHROMA_EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MIN_SIMILARITY = 0.35
MIN_KEYWORD_OVERLAP = 0.12
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "is", "it", "of", "on", "or", "our", "policy", "please",
    "the", "to", "was", "what", "when", "where", "which", "who", "why",
    "with", "you", "your",
}


@contextmanager
def _disable_proxy_env():
    proxy_keys = [key for key in os.environ if "PROXY" in key.upper()]
    saved = {key: os.environ.pop(key, None) for key in proxy_keys}
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value


def _embeddings():
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def _client():
    if not CHROMA_API_KEY:
        raise RuntimeError("Set CHROMA_API_KEY to save data in Chroma Cloud.")
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError(
            "ChromaDB is unavailable. Install compatible chromadb and opentelemetry packages to use the knowledge base."
        ) from exc
    with _disable_proxy_env():
        return chromadb.CloudClient(
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
            api_key=CHROMA_API_KEY,
        )


def _collection():
    return _client().get_or_create_collection(name=CHROMA_COLLECTION)


def _safe_filename(name):
    stem, suffix = os.path.splitext(name or "")
    stem = stem or "knowledge_file"
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", stem).strip("_.-") or "knowledge_file"
    return f"{safe}{suffix}"


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def _important_tokens(text):
    return {token for token in _tokens(text) if len(token) > 2 and token not in STOPWORDS}


def _keyword_overlap(query, text):
    q = _important_tokens(query)
    t = _important_tokens(text)
    return len(q & t) / len(q) if q and t else 0.0


def _read_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()


def _load_source_docs(file_bytes, filename, title, preview_text=""):
    suffix = os.path.splitext(filename or "")[1].lower()
    if suffix == ".pdf":
        text = _read_pdf(file_bytes)
        return [Document(page_content=text or preview_text or title or "")]
    if suffix in {".txt", ".md", ".csv", ".json", ".py", ".js", ".jsx", ".ts", ".tsx"}:
        text = (file_bytes or b"").decode("utf-8", errors="ignore").strip()
        return [Document(page_content=text or preview_text or title or "")]
    return [Document(page_content=preview_text or title or "")]


def _tag_chunks(docs, doc_id, title, filename, stored_path, created_at):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs) or [Document(page_content=title or "")]
    for index, chunk in enumerate(chunks):
        chunk.metadata.update({
            "doc_id": doc_id,
            "title": title,
            "file_name": filename or "",
            "stored_file": str(stored_path) if stored_path else "",
            "chunk_index": index,
            "created_at": created_at,
        })
    return chunks


def upsert_knowledge_document(title, file_bytes=None, filename=None, preview_text=""):
    try:
        collection = _collection()
    except Exception as exc:
        raise RuntimeError(
            "Knowledge base is unavailable because ChromaDB/opentelemetry is not compatible in this environment."
        ) from exc
    doc_id = uuid.uuid4().hex
    created_at = datetime.now(timezone.utc).isoformat()
    original_name = filename or f"{title or 'knowledge_note'}.txt"
    safe_name = _safe_filename(f"{doc_id}_{original_name}")
    file_bytes = file_bytes or (preview_text or title or "").encode("utf-8")

    source_docs = _load_source_docs(file_bytes, filename or safe_name, title or original_name, preview_text)
    chunks = _tag_chunks(source_docs, doc_id, title or original_name, filename, None, created_at)
    texts = [chunk.page_content or "" for chunk in chunks]
    metadatas = [chunk.metadata or {} for chunk in chunks]
    embeddings = _embeddings().embed_documents(texts)
    ids = [f"{doc_id}_{index}" for index in range(len(chunks))]
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    return {
        "document_id": doc_id,
        "title": title or original_name,
        "file_name": filename or "",
        "stored_file": "",
        "chunks": len(chunks),
        "created_at": created_at,
    }


def search_knowledge_base(query, top_k=5):
    try:
        collection = _collection()
    except Exception:
        return {"found": False, "hits": [], "context": ""}
    if not query or not query.strip() or collection.count() == 0:
        return {"found": False, "hits": [], "context": ""}

    query_lower = query.lower().strip()
    query_embedding = _embeddings().embed_query(query)

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=max(top_k, 8),
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    docs = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    hits = []
    context_parts = []

    for text, md, dist in zip(docs, metadatas, distances):
        md = md or {}
        text = text or ""
        combined = f"{md.get('title', '')}\n{text}"
        keyword_overlap = _keyword_overlap(query, combined)
        exact_match = query_lower in combined.lower()
        similarity = max(0.0, min(1.0, 1.0 - float(dist or 0.0)))

        if exact_match:
            similarity = max(similarity, 0.98)
        elif keyword_overlap:
            similarity = max(similarity, min(0.95, keyword_overlap + 0.2))

        hit = {
            "text": text,
            "title": md.get("title", ""),
            "doc_id": md.get("doc_id", ""),
            "file_name": md.get("file_name", ""),
            "chunk_index": md.get("chunk_index", 0),
            "similarity": round(similarity, 4),
            "keyword_overlap": round(keyword_overlap, 4),
        }
        hits.append(hit)
        if exact_match or keyword_overlap >= MIN_KEYWORD_OVERLAP or similarity >= MIN_SIMILARITY:
            context_parts.append(f"[{hit['title']}] {text}")

    return {"found": bool(context_parts), "hits": hits[:top_k], "context": "\n\n".join(context_parts[:top_k]).strip()}


def answer_from_knowledge_base(query):
    result = search_knowledge_base(query)
    if not result["found"] or not result["context"]:
        return None, result

    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0)
    response = llm.invoke([
        (
            "system",
            "Answer only using the provided context. "
            "If the answer is not clearly present in the context, reply exactly with NOT_FOUND. "
            "Do not mention the knowledge base or source.",
        ),
        ("user", f"Question: {query}\n\nContext:\n{result['context']}"),
    ])
    answer = (response.content or "").strip()
    if not answer or answer.upper() == "NOT_FOUND":
        return None, result
    return answer, result


def list_knowledge_documents():
    try:
        collection = _collection()
    except Exception:
        return []
    if collection.count() == 0:
        return []

    data = collection.get(include=["documents", "metadatas"])
    docs = data.get("documents") or []
    metadatas = data.get("metadatas") or []
    grouped = {}

    for index, md in enumerate(metadatas):
        md = md or {}
        doc_id = md.get("doc_id")
        if not doc_id:
            continue
        item = grouped.setdefault(doc_id, {
            "document_id": doc_id,
            "title": md.get("title", ""),
            "file_name": md.get("file_name", ""),
            "stored_file": "",
            "chunks": 0,
            "created_at": md.get("created_at", ""),
            "preview": (docs[index] if index < len(docs) else "")[:300],
        })
        item["chunks"] += 1

    return list(grouped.values())


def delete_knowledge_document(document_id):
    if not document_id:
        raise ValueError("document_id is required")

    try:
        collection = _collection()
    except Exception as exc:
        raise RuntimeError(
            "Knowledge base is unavailable because ChromaDB/opentelemetry is not compatible in this environment."
        ) from exc
    data = collection.get(where={"doc_id": document_id}, include=["metadatas"])
    metadatas = data.get("metadatas") or []
    collection.delete(where={"doc_id": document_id})

    return {"deleted": True, "document_id": document_id, "removed_chunks": len(metadatas)}
