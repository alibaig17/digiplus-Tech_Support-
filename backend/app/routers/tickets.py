"""
🎫 Ticket management — CRUD, screenshot upload & AI analysis, duplicate detection.
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from bson import ObjectId

from app.database import tickets_col
from app.models.schemas import TicketUpdate, TicketStatus, TicketPriority
from app.auth.dependencies import get_current_user
from app.config import settings
from app.services import gemini_service, ocr_service, vector_service

router = APIRouter(prefix="/tickets", tags=["tickets"])

os.makedirs(settings.upload_dir, exist_ok=True)


def _serialize(t: dict) -> dict:
    t = dict(t)
    t["id"] = str(t.pop("_id"))
    return t


@router.post("")
async def create_ticket(
    title: str = Form(...),
    description: str = Form(...),
    reporter_name: str = Form(...),
    reporter_email: str = Form(...),
    category: str = Form("General"),
    priority: str = Form("Medium"),
    screenshot: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
):
    screenshot_url = None
    ocr_text = ""

    if screenshot is not None:
        ext = os.path.splitext(screenshot.filename)[1] or ".png"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(settings.upload_dir, filename)
        contents = await screenshot.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        screenshot_url = f"/uploads/{filename}"
        ocr_text = ocr_service.extract_text(filepath)

    now = datetime.utcnow()
    doc = {
        "title": title,
        "description": description,
        "reporter_name": reporter_name,
        "reporter_email": reporter_email,
        "status": "Open",
        "priority": priority,
        "category": category,
        "screenshot_url": screenshot_url,
        "ocr_text": ocr_text,
        "ai_analysis": None,
        "created_by": user["id"],
        "created_at": now,
        "updated_at": now,
    }
    result = await tickets_col.insert_one(doc)
    ticket_id = str(result.inserted_id)

    # 🤖 Auto-run AI analysis (summary/category/priority/root cause/impact scores)
    analysis = gemini_service.analyze_ticket(title, description, ocr_text)
    await tickets_col.update_one({"_id": result.inserted_id}, {"$set": {"ai_analysis": analysis}})

    # 📐 Index in vector store for future similarity/duplicate search
    vector_service.upsert_ticket_vector(ticket_id, title, description, status="Open")

    # ⚠️ Duplicate / similar incident detection
    similar = vector_service.find_similar(f"{title}\n{description}", top_k=5, exclude_id=ticket_id)

    ticket = await tickets_col.find_one({"_id": result.inserted_id})
    out = _serialize(ticket)
    out["similar_incidents"] = similar
    return out


@router.get("")
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    user: dict = Depends(get_current_user),
):
    query = {}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if category:
        query["category"] = category
    cursor = tickets_col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    tickets = [_serialize(t) async for t in cursor]
    total = await tickets_col.count_documents(query)
    return {"tickets": tickets, "total": total}


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str, user: dict = Depends(get_current_user)):
    ticket = await tickets_col.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return _serialize(ticket)


@router.put("/{ticket_id}")
async def update_ticket(ticket_id: str, payload: TicketUpdate, user: dict = Depends(get_current_user)):
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")
    update["updated_at"] = datetime.utcnow()
    result = await tickets_col.update_one({"_id": ObjectId(ticket_id)}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket = await tickets_col.find_one({"_id": ObjectId(ticket_id)})
    vector_service.upsert_ticket_vector(
        ticket_id, ticket["title"], ticket["description"], status=ticket.get("status", "Open")
    )
    return _serialize(ticket)


@router.delete("/{ticket_id}")
async def delete_ticket(ticket_id: str, user: dict = Depends(get_current_user)):
    result = await tickets_col.delete_one({"_id": ObjectId(ticket_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "🗑️ Ticket deleted"}


@router.post("/{ticket_id}/analyze")
async def analyze_ticket(ticket_id: str, user: dict = Depends(get_current_user)):
    """🧠 Re-run AI analysis (summary, category, priority, root cause, impact scores)."""
    ticket = await tickets_col.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ocr_text = ticket.get("ocr_text", "")
    analysis = gemini_service.analyze_ticket(ticket["title"], ticket["description"], ocr_text)
    await tickets_col.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": {"ai_analysis": analysis, "updated_at": datetime.utcnow()}},
    )
    similar = vector_service.find_similar(
        f"{ticket['title']}\n{ticket['description']}", top_k=5, exclude_id=ticket_id
    )
    return {"ai_analysis": analysis, "similar_incidents": similar}
