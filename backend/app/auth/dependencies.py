"""
🛂 Auth dependencies — resolve the current user from a Bearer JWT.

The frontend login/OTP flow has been removed for local dev, so no token is
ever sent. When that's the case, we fall back to a fixed dev user instead
of rejecting the request. If a real token IS sent, it's still validated
normally.
"""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from typing import Optional

from app.utils.security import decode_access_token
from app.database import users_col

bearer_scheme = HTTPBearer(auto_error=False)

# Dev fallback — used only when no Authorization header is present at all.
_DEV_USER = {
    "id": "dev-user",
    "_id": "dev-user",
    "name": "Dev User",
    "email": "dev@example.com",
    "role": "admin",
}


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    if creds is None:
        return dict(_DEV_USER)

    payload = decode_access_token(creds.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token 🔒")
    user = await users_col.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user["id"] = str(user["_id"])
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required 🚫")
    return user
