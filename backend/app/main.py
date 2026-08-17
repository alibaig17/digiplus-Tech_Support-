"""
🚀 AI Support Copilot — FastAPI entrypoint.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import ensure_indexes
from app.routers import auth, tickets, assistant, search, knowledge_base, analytics, users
from app.auth.dependencies import get_current_user
from app.models.schemas import UserOut

app = FastAPI(
    title="🚀 AI Support Copilot API",
    description="AI-powered support desk: tickets, screenshot analysis, AI assistant, KB, search & analytics.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "https://digiplus-tech-support.vercel.app","http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(assistant.router)
app.include_router(search.router)
app.include_router(knowledge_base.router)
app.include_router(analytics.router)
app.include_router(users.router)


@app.on_event("startup")
async def on_startup():
    await ensure_indexes()
    print("✅ AI Support Copilot backend started")


@app.get("/")
async def root():
    return {"message": "🚀 AI Support Copilot API is running", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Spec calls for a root-level GET /me (in addition to /auth/me)
@app.get("/me", response_model=UserOut)
async def me_alias(user: dict = Depends(get_current_user)):
    return UserOut(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user.get("role", "engineer"),
        created_at=user.get("createdAt"),
    )
