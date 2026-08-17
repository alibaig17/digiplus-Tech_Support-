"""
🔎 Historical incident search — combines MongoDB text search with ChromaDB
semantic similarity so results include a similarity %, past issue, resolution
and status, as required by the spec.
"""
from fastapi import APIRouter, Depends, Query
from app.database import tickets_col, resolutions_col
from app.auth.dependencies import get_current_user
from app.services import vector_service

router = APIRouter(tags=["search"])


@router.get("/search")
async def search_incidents(q: str = Query(..., min_length=1), user: dict = Depends(get_current_user)):
    # 1️⃣ Semantic similarity via ChromaDB (title/description/resolution embeddings)
    semantic_results = vector_service.find_similar(q, top_k=10)

    # 2️⃣ Fallback / supplement with MongoDB full-text search
    text_hits = []
    try:
        cursor = tickets_col.find({"$text": {"$search": q}}, {"score": {"$meta": "textScore"}}).sort(
            [("score", {"$meta": "textScore"})]
        ).limit(10)
        async for t in cursor:
            text_hits.append(t)
    except Exception:
        pass

    seen_ids = {r["ticket_id"] for r in semantic_results}
    results = list(semantic_results)

    for t in text_hits:
        tid = str(t["_id"])
        if tid in seen_ids:
            continue
        resolution_doc = await resolutions_col.find_one({"ticket_id": tid}, sort=[("created_at", -1)])
        results.append(
            {
                "ticket_id": tid,
                "title": t["title"],
                "resolution": resolution_doc["resolution_summary"] if resolution_doc else None,
                "status": t.get("status", "Open"),
                "similarity": 60.0,  # heuristic score for text-match-only hits
            }
        )
        seen_ids.add(tid)

    # Enrich semantic results with resolution + status from DB if missing
    for r in results:
        if r.get("resolution") is None:
            res_doc = await resolutions_col.find_one({"ticket_id": r["ticket_id"]}, sort=[("created_at", -1)])
            if res_doc:
                r["resolution"] = res_doc["resolution_summary"]

    results.sort(key=lambda r: r["similarity"], reverse=True)
    return {"query": q, "results": results[:15]}
