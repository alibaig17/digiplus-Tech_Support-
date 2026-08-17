"""
👥 User management — admin only. No public registration: admins add users
here (or directly in MongoDB Atlas) and they become eligible for OTP login.
"""
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Literal

from app.database import users_col
from app.auth.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: Literal["admin", "engineer"] = "engineer"


def _serialize(u: dict) -> dict:
    u = dict(u)
    u["id"] = str(u.pop("_id"))
    return u


@router.get("")
async def list_users(user: dict = Depends(require_admin)):
    cursor = users_col.find({})
    return {"users": [_serialize(u) async for u in cursor]}


@router.post("")
async def create_user(payload: UserCreate, user: dict = Depends(require_admin)):
    existing = await users_col.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    doc = {
        "name": payload.name,
        "email": payload.email.lower(),
        "role": payload.role,
        "createdAt": datetime.utcnow(),
    }
    result = await users_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.delete("/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(require_admin)):
    result = await users_col.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "🗑️ User removed"}
