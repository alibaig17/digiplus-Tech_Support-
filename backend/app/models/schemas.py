"""
📦 Pydantic schemas — request/response contracts for the whole API.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr, Field


def now() -> datetime:
    return datetime.utcnow()


# ---------- Auth ----------
class SendOtpRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Literal["admin", "engineer"]
    created_at: datetime


# ---------- Tickets ----------
TicketStatus = Literal["Open", "In Progress", "Resolved"]
TicketPriority = Literal["Low", "Medium", "High", "Critical"]


class TicketCreate(BaseModel):
    title: str
    description: str
    reporter_name: str
    reporter_email: EmailStr
    category: Optional[str] = "General"
    priority: Optional[TicketPriority] = "Medium"


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[str] = None


class AIAnalysis(BaseModel):
    summary: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    root_cause: Optional[str] = None
    suggested_resolution: Optional[str] = None
    business_impact_score: Optional[int] = None
    urgency_score: Optional[int] = None
    complexity_score: Optional[int] = None
    root_cause_prediction: Optional[str] = None


class TicketOut(BaseModel):
    id: str
    title: str
    description: str
    screenshot_url: Optional[str] = None
    reporter_name: str
    reporter_email: EmailStr
    status: TicketStatus
    priority: TicketPriority
    category: str
    ai_analysis: Optional[AIAnalysis] = None
    created_at: datetime
    updated_at: datetime


# ---------- AI Assistant chat ----------
class AssistantMessageRequest(BaseModel):
    message: str


class ChatMessageOut(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


# ---------- Resolutions ----------
class ResolutionCreate(BaseModel):
    root_cause: str
    actions_taken: str
    resolution_summary: str
    outcome: str


class ResolutionOut(ResolutionCreate):
    ticket_id: str
    resolved_by: Optional[str] = None
    created_at: datetime


# ---------- Knowledge base ----------
class KBCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class KBUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class KBOut(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime


# ---------- Search ----------
class SearchResult(BaseModel):
    ticket_id: str
    title: str
    resolution: Optional[str] = None
    status: str
    similarity: float


# ---------- Analytics ----------
class AnalyticsOverview(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    critical_tickets: int
    by_status: dict
    by_category: dict
    by_priority: dict
    most_common_issues: List[dict]
