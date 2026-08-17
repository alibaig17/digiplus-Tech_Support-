"""
🤖 Gemini 2.5 Flash integration.

Centralizes every AI call the app makes:
- screenshot/ticket analysis (summary, category, priority, root cause)
- impact/urgency/complexity scoring
- AI assistant chat (troubleshooting)
- resolution generation
"""
import json
import re
import google.generativeai as genai
from app.config import settings

_configured = False


def _client():
    global _configured
    if not _configured:
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
        _configured = True
    return genai.GenerativeModel(settings.gemini_model)


def _extract_json(text: str) -> dict:
    """Gemini sometimes wraps JSON in ```json fences — strip and parse safely."""
    cleaned = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except Exception:
        return {"raw": text}


def _safe_generate(prompt: str) -> str:
    if not settings.gemini_api_key:
        return "⚠️ Gemini API key not configured. Add GEMINI_API_KEY to backend/.env to enable AI features."
    try:
        model = _client()
        response = model.generate_content(prompt)
        return response.text or ""
    except Exception as e:
        return f"⚠️ AI generation failed: {e}"


def analyze_ticket(title: str, description: str, ocr_text: str = "") -> dict:
    """🧠 Generate summary/category/priority/root-cause + impact scores for a ticket."""
    prompt = f"""
You are an expert IT support triage assistant. Analyze this support ticket and respond
ONLY with strict JSON (no markdown, no commentary) matching this exact shape:

{{
  "summary": "<1-2 sentence summary>",
  "category": "<one of: Network, Software, Hardware, Access/Auth, Email, Browser, VS Code/Dev Tools, Application Crash, Other>",
  "priority": "<one of: Low, Medium, High, Critical>",
  "root_cause": "<best-guess root cause, 1-2 sentences>",
  "suggested_resolution": "<concrete suggested fix, 2-3 sentences>",
  "business_impact_score": <integer 0-100>,
  "urgency_score": <integer 0-100>,
  "complexity_score": <integer 0-100>,
  "root_cause_prediction": "<short root cause label, e.g. 'Expired MFA token'>"
}}

Ticket title: {title}
Ticket description: {description}
OCR text extracted from an attached screenshot (may be empty): {ocr_text}
"""
    raw = _safe_generate(prompt)
    return _extract_json(raw)


def analyze_screenshot(ocr_text: str) -> dict:
    """🖼️ Analyze OCR'd screenshot text into a structured triage report."""
    prompt = f"""
You are analyzing OCR text extracted from a screenshot of a technical error
(could be Outlook, a browser, VS Code, a terminal, a login screen, or an app crash).
Respond ONLY with strict JSON:

{{
  "summary": "<what error is shown>",
  "category": "<short category label>",
  "priority": "<Low|Medium|High|Critical>",
  "root_cause": "<likely root cause>",
  "suggested_resolution": "<concrete fix suggestion>"
}}

OCR TEXT:
{ocr_text}
"""
    raw = _safe_generate(prompt)
    return _extract_json(raw)


def ai_assistant_reply(
    ticket_title: str,
    ticket_description: str,
    ai_analysis: dict,
    similar_incidents: list,
    kb_articles: list,
    chat_history: list,
    user_message: str,
) -> str:
    """💬 Conversational troubleshooting assistant, grounded in ticket + KB + similar incidents."""
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in chat_history[-10:]
    )
    similar_text = "\n".join(
        f"- {i.get('title')} (resolution: {i.get('resolution', 'N/A')})" for i in similar_incidents
    ) or "None found."
    kb_text = "\n".join(f"- {k.get('title')}: {k.get('content')[:200]}" for k in kb_articles) or "None found."

    prompt = f"""
You are an AI Support Copilot helping a support engineer investigate and resolve a ticket.
Be concise, practical, and structured. Use bullet points. Reference relevant knowledge base
articles or similar past incidents when useful.

TICKET: {ticket_title}
DESCRIPTION: {ticket_description}
AI ANALYSIS: {json.dumps(ai_analysis)}

SIMILAR PAST INCIDENTS:
{similar_text}

RELEVANT KNOWLEDGE BASE ARTICLES:
{kb_text}

CONVERSATION SO FAR:
{history_text}

ENGINEER'S NEW MESSAGE: {user_message}

Respond with:
1. Investigation steps
2. Root cause analysis
3. Suggested fixes
4. Troubleshooting workflow (numbered)
"""
    return _safe_generate(prompt)


def generate_resolution(ticket_title: str, description: str, ai_analysis: dict, chat_history: list) -> dict:
    """✅ Draft a resolution the engineer can edit before saving."""
    history_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in chat_history[-10:])
    prompt = f"""
Based on this resolved support ticket, draft a resolution report.
Respond ONLY with strict JSON:

{{
  "root_cause": "<final root cause>",
  "actions_taken": "<what was done to fix it>",
  "resolution_summary": "<short summary>",
  "outcome": "<result / confirmation the issue is fixed>"
}}

TICKET: {ticket_title}
DESCRIPTION: {description}
AI ANALYSIS: {json.dumps(ai_analysis)}
CHAT HISTORY:
{history_text}
"""
    raw = _safe_generate(prompt)
    return _extract_json(raw)


def embed_text(text: str) -> list:
    """📐 Generate an embedding vector for semantic search / duplicate detection."""
    if not settings.gemini_api_key:
        return []
    try:
        result = genai.embed_content(model="models/text-embedding-004", content=text)
        return result["embedding"]
    except Exception as e:
        print(f"⚠️ Embedding failed: {e}")
        return []
