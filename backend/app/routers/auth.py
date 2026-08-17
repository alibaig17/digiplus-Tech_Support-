"""
🔐 Auth routes — Email OTP login (via Brevo) + JWT issuance.

No public registration: users must already exist in the `users` collection
(added manually / via seed script) for login to succeed.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends

from app.database import users_col, otp_col
from app.models.schemas import SendOtpRequest, VerifyOtpRequest, TokenResponse, UserOut
from app.utils.security import generate_otp, create_access_token
from app.services.brevo_service import send_otp_email
from app.config import settings
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp")
async def send_otp(payload: SendOtpRequest):
    user = await users_col.find_one({"email": payload.email.lower()})
    if not user:
        # Deliberately vague to avoid leaking which emails are registered.
        raise HTTPException(status_code=404, detail="Email not recognized. Contact your admin. 🚫")

    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)
    await otp_col.insert_one(
        {"email": payload.email.lower(), "otp": otp, "expires_at": expires_at, "used": False}
    )
    send_otp_email(payload.email, user.get("name", ""), otp)
    return {"message": f"📧 OTP sent to {payload.email}", "expires_in_minutes": settings.otp_expire_minutes}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(payload: VerifyOtpRequest):
    record = await otp_col.find_one(
        {"email": payload.email.lower(), "otp": payload.otp, "used": False},
        sort=[("_id", -1)],
    )
    if not record:
        raise HTTPException(status_code=400, detail="Invalid OTP ❌")
    if record["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired ⏰. Please request a new one.")

    await otp_col.update_one({"_id": record["_id"]}, {"$set": {"used": True}})

    user = await users_col.find_one({"email": payload.email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_access_token({"sub": str(user["_id"]), "role": user.get("role", "engineer")})
    user_out = UserOut(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user.get("role", "engineer"),
        created_at=user.get("createdAt", datetime.utcnow()),
    )
    return TokenResponse(access_token=token, user=user_out)


@router.get("/me", response_model=UserOut)
async def me(user: dict = Depends(get_current_user)):
    return UserOut(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user.get("role", "engineer"),
        created_at=user.get("createdAt", datetime.utcnow()),
    )
