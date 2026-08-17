"""
🤖 AI Assistant — per-ticket chat that grounds Gemini in the ticket, similar
incidents, and knowledge base articles. Also handles resolve + resolution
report generation.
"""
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import tickets_col, chats_col, resolutions_col, kb_col
from app.models.schemas import AssistantMessageRequest, ResolutionCreate
from app.auth.dependencies import get_current_user
from app.services import gemini_service, vector_service

router = APIRouter(prefix="/tickets", tags=["assistant"])


async def _get_ticket_or_404(ticket_id: str) -> dict:
    ticket = await tickets_col.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/{ticket_id}/assistant")
async def get_chat_history(ticket_id: str, user: dict = Depends(get_current_user)):
    cursor = chats_col.find({"ticket_id": ticket_id}).sort("created_at", 1)
    messages = [{"role": m["role"], "content": m["content"], "created_at": m["created_at"]} async for m in cursor]
    return {"messages": messages}


@router.post("/{ticket_id}/assistant")
async def ask_assistant(ticket_id: str, payload: AssistantMessageRequest, user: dict = Depends(get_current_user)):
    """💬 Ask the AI Assistant — grounded in ticket, similar incidents & KB."""
    ticket = await _get_ticket_or_404(ticket_id)

    # Save user message
    await chats_col.insert_one(
        {"ticket_id": ticket_id, "role": "user", "content": payload.message, "created_at": datetime.utcnow()}
    )

    history_cursor = chats_col.find({"ticket_id": ticket_id}).sort("created_at", 1)
    history = [{"role": m["role"], "content": m["content"]} async for m in history_cursor]

    similar_incidents = vector_service.find_similar(
        f"{ticket['title']}\n{ticket['description']}", top_k=3, exclude_id=ticket_id
    )

    kb_cursor = kb_col.find({"$text": {"$search": ticket["title"]}}).limit(3)
    kb_articles = []
    try:
        kb_articles = [{"title": k["title"], "content": k["content"]} async for k in kb_cursor]
    except Exception:
        pass  # text index may not exist yet on empty collection

    reply = gemini_service.ai_assistant_reply(
        ticket_title=ticket["title"],
        ticket_description=ticket["description"],
        ai_analysis=ticket.get("ai_analysis") or {},
        similar_incidents=similar_incidents,
        kb_articles=kb_articles,
        chat_history=history,
        user_message=payload.message,
    )

    await chats_col.insert_one(
        {"ticket_id": ticket_id, "role": "assistant", "content": reply, "created_at": datetime.utcnow()}
    )
    return {"reply": reply, "similar_incidents": similar_incidents}


@router.post("/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, payload: ResolutionCreate | None = None, user: dict = Depends(get_current_user)):
    """✅ Resolve a ticket. If no resolution body is given, AI drafts one first."""
    ticket = await _get_ticket_or_404(ticket_id)

    if payload is None:
        history_cursor = chats_col.find({"ticket_id": ticket_id}).sort("created_at", 1)
        history = [{"role": m["role"], "content": m["content"]} async for m in history_cursor]
        draft = gemini_service.generate_resolution(
            ticket["title"], ticket["description"], ticket.get("ai_analysis") or {}, history
        )
        return {"draft": draft, "message": "✍️ Draft generated — review and POST again to save."}

    doc = {
        "ticket_id": ticket_id,
        **payload.model_dump(),
        "resolved_by": user["id"],
        "created_at": datetime.utcnow(),
    }
    await resolutions_col.insert_one(doc)
    await tickets_col.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": {"status": "Resolved", "updated_at": datetime.utcnow()}},
    )
    vector_service.upsert_ticket_vector(
        ticket_id, ticket["title"], ticket["description"], resolution=payload.resolution_summary, status="Resolved"
    )
    return {"message": "✅ Ticket resolved", "resolution": doc}


@router.get("/{ticket_id}/resolution")
async def get_resolution(ticket_id: str, user: dict = Depends(get_current_user)):
    res = await resolutions_col.find_one({"ticket_id": ticket_id}, sort=[("created_at", -1)])
    if not res:
        raise HTTPException(status_code=404, detail="No resolution recorded yet")
    res["_id"] = str(res["_id"])
    return res
