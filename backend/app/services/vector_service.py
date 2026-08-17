"""
📐 ChromaDB vector store — powers semantic search & duplicate-incident detection.

We embed a ticket's title+description (+resolution once resolved) and store
it in a persistent Chroma collection keyed by ticket_id, so we can query
"which past tickets look like this one?" using nearest-neighbor search.
"""
import chromadb
from app.config import settings
from app.services.gemini_service import embed_text

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        _collection = _client.get_or_create_collection(name="tickets")
    return _collection


def upsert_ticket_vector(ticket_id: str, title: str, description: str, resolution: str = "", status: str = "Open"):
    """Add/update a ticket's embedding in the vector store."""
    text = f"{title}\n{description}\n{resolution}".strip()
    embedding = embed_text(text)
    if not embedding:
        return  # Gemini not configured — skip silently, search falls back to text search
    collection = _get_collection()
    collection.upsert(
        ids=[ticket_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"title": title, "resolution": resolution or "", "status": status}],
    )


def find_similar(text: str, top_k: int = 5, exclude_id: str = None) -> list:
    """🔎 Return the top-k most similar past tickets to the given text."""
    embedding = embed_text(text)
    if not embedding:
        return []
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(query_embeddings=[embedding], n_results=min(top_k + 1, count))
    output = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for i, tid in enumerate(ids):
        if exclude_id and tid == exclude_id:
            continue
        distance = distances[i]
        similarity = max(0.0, 1 - distance / 2)  # cosine-ish distance -> similarity 0..1
        meta = metadatas[i]
        output.append(
            {
                "ticket_id": tid,
                "title": meta.get("title", ""),
                "resolution": meta.get("resolution", ""),
                "status": meta.get("status", ""),
                "similarity": round(similarity * 100, 1),
            }
        )
    return output[:top_k]
