"""
📚 Knowledge base CRUD. Admins manage articles; the AI assistant searches
this collection before generating answers.
"""
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import kb_col
from app.models.schemas import KBCreate, KBUpdate
from app.auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/kb", tags=["knowledge-base"])


def _serialize(a: dict) -> dict:
    a = dict(a)
    a["id"] = str(a.pop("_id"))
    return a


@router.get("")
async def list_articles(q: str = None, user: dict = Depends(get_current_user)):
    query = {}
    if q:
        query = {"$text": {"$search": q}}
    cursor = kb_col.find(query).sort("created_at", -1)
    return {"articles": [_serialize(a) async for a in cursor]}


@router.get("/{article_id}")
async def get_article(article_id: str, user: dict = Depends(get_current_user)):
    a = await kb_col.find_one({"_id": ObjectId(article_id)})
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    return _serialize(a)


@router.post("")
async def create_article(payload: KBCreate, user: dict = Depends(require_admin)):
    now = datetime.utcnow()
    doc = {**payload.model_dump(), "created_at": now, "updated_at": now, "created_by": user["id"]}
    result = await kb_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.put("/{article_id}")
async def update_article(article_id: str, payload: KBUpdate, user: dict = Depends(require_admin)):
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    update["updated_at"] = datetime.utcnow()
    result = await kb_col.update_one({"_id": ObjectId(article_id)}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    a = await kb_col.find_one({"_id": ObjectId(article_id)})
    return _serialize(a)


@router.delete("/{article_id}")
async def delete_article(article_id: str, user: dict = Depends(require_admin)):
    result = await kb_col.delete_one({"_id": ObjectId(article_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "🗑️ Article deleted"}
