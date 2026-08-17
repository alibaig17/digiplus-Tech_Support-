"""
🎫 Seed sample tickets from the HuggingFace dataset:
    https://huggingface.co/datasets/mindweave/help-desk-tickets

Loads the "tickets" config/subset, normalizes flexible column names into our
ticket schema, and inserts a sample of rows into MongoDB. Optionally indexes
each ticket into ChromaDB for search/duplicate-detection out of the box.

Run:
    python -m seed.seed_tickets --limit 150
    python -m seed.seed_tickets --limit 150 --with-embeddings   # slower, needs GEMINI_API_KEY

If the dataset can't be downloaded (no internet / HF auth issue), a small
built-in fallback sample is used instead so the app is still demoable.
"""
import argparse
import asyncio
import os
import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import tickets_col, resolutions_col  # noqa: E402
from app.services import vector_service  # noqa: E402

STATUSES = ["Open", "In Progress", "Resolved"]
PRIORITY_MAP = {
    "p1": "Critical", "p2": "High", "p3": "Medium", "p4": "Low",
    "critical": "Critical", "high": "High", "medium": "Medium", "low": "Low",
}

FALLBACK_TICKETS = [
    {"title": "Outlook authentication failure", "description": "User cannot sign into Outlook, MFA prompt loops repeatedly.", "category": "Email", "priority": "High"},
    {"title": "VPN disconnects every 10 minutes", "description": "Remote employee's VPN client drops connection intermittently during work hours.", "category": "Network", "priority": "Medium"},
    {"title": "VS Code extension crashing on startup", "description": "Python extension throws an unhandled exception when opening any workspace.", "category": "VS Code/Dev Tools", "priority": "Low"},
    {"title": "Application crash on login", "description": "Internal CRM app crashes immediately after entering credentials.", "category": "Application Crash", "priority": "Critical"},
    {"title": "Browser rendering issue in Chrome", "description": "Internal dashboard displays broken CSS only in Chrome, works fine in Firefox.", "category": "Browser", "priority": "Low"},
    {"title": "Terminal permission denied error", "description": "Deploy script fails with 'permission denied' when writing to /var/log.", "category": "Software", "priority": "Medium"},
    {"title": "Password reset email not received", "description": "User requested a password reset but no email arrived after 20 minutes.", "category": "Access/Auth", "priority": "Medium"},
    {"title": "Printer not detected on network", "description": "Office printer no longer shows up in the network printer list.", "category": "Hardware", "priority": "Low"},
]


def _norm_priority(val) -> str:
    if not val:
        return random.choice(["Low", "Medium", "High", "Critical"])
    v = str(val).strip().lower()
    return PRIORITY_MAP.get(v, v.title() if v.title() in ["Low", "Medium", "High", "Critical"] else "Medium")


def _norm_status(val) -> str:
    if not val:
        return random.choice(STATUSES)
    v = str(val).strip().lower()
    if "open" in v or "new" in v:
        return "Open"
    if "progress" in v or "assign" in v or "pending" in v:
        return "In Progress"
    if "resolv" in v or "closed" in v or "done" in v:
        return "Resolved"
    return random.choice(STATUSES)


def _first_present(row: dict, candidates: list, default=None):
    for c in candidates:
        if c in row and row[c] not in (None, ""):
            return row[c]
    return default


def load_from_huggingface(limit: int):
    """Try to load the real dataset via the `datasets` library."""
    from datasets import load_dataset

    ds = load_dataset("mindweave/help-desk-tickets", "tickets", split="train")
    rows = ds.select(range(min(limit, len(ds))))
    normalized = []
    for row in rows:
        title = _first_present(row, ["subject", "title", "summary", "short_description"], "Untitled ticket")
        description = _first_present(row, ["description", "body", "text", "details"], title)
        category = _first_present(row, ["category", "category_name", "type"], "General")
        priority = _norm_priority(_first_present(row, ["priority", "priority_level"]))
        status = _norm_status(_first_present(row, ["status", "state"]))
        resolution = _first_present(row, ["resolution", "resolution_notes", "solution"])
        normalized.append(
            {
                "title": str(title)[:200],
                "description": str(description),
                "category": str(category),
                "priority": priority,
                "status": status,
                "resolution": str(resolution) if resolution else None,
            }
        )
    return normalized


def load_fallback(limit: int):
    data = []
    for i in range(limit):
        base = FALLBACK_TICKETS[i % len(FALLBACK_TICKETS)]
        data.append(
            {
                "title": base["title"],
                "description": base["description"],
                "category": base["category"],
                "priority": base["priority"],
                "status": random.choice(STATUSES),
                "resolution": None,
            }
        )
    return data


async def run(limit: int, with_embeddings: bool):
    try:
        print("⬇️  Downloading mindweave/help-desk-tickets from HuggingFace...")
        rows = load_from_huggingface(limit)
        print(f"✅ Loaded {len(rows)} rows from HuggingFace dataset")
    except Exception as e:
        print(f"⚠️ Could not load HuggingFace dataset ({e}). Using built-in fallback sample instead.")
        rows = load_fallback(limit)

    inserted = 0
    now = datetime.utcnow()
    for i, row in enumerate(rows):
        created_at = now - timedelta(days=random.randint(0, 180), hours=random.randint(0, 23))
        doc = {
            "title": row["title"],
            "description": row["description"],
            "reporter_name": "Sample User",
            "reporter_email": "sample.user@example.com",
            "status": row["status"],
            "priority": row["priority"],
            "category": row["category"],
            "screenshot_url": None,
            "ocr_text": "",
            "ai_analysis": None,
            "created_by": "seed-script",
            "created_at": created_at,
            "updated_at": created_at,
        }
        result = await tickets_col.insert_one(doc)
        ticket_id = str(result.inserted_id)

        if row["status"] == "Resolved" and row.get("resolution"):
            await resolutions_col.insert_one(
                {
                    "ticket_id": ticket_id,
                    "root_cause": "See resolution notes",
                    "actions_taken": row["resolution"],
                    "resolution_summary": row["resolution"][:300],
                    "outcome": "Resolved",
                    "resolved_by": "seed-script",
                    "created_at": created_at,
                }
            )

        if with_embeddings:
            vector_service.upsert_ticket_vector(
                ticket_id, row["title"], row["description"], resolution=row.get("resolution") or "", status=row["status"]
            )

        inserted += 1
        if inserted % 25 == 0:
            print(f"  ...inserted {inserted}/{len(rows)}")

    print(f"\n🎉 Seeded {inserted} tickets into MongoDB.")
    if not with_embeddings:
        print("ℹ️  Skipped ChromaDB embeddings (pass --with-embeddings and set GEMINI_API_KEY to enable).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=150, help="Number of tickets to seed")
    parser.add_argument("--with-embeddings", action="store_true", help="Also embed tickets into ChromaDB")
    args = parser.parse_args()
    asyncio.run(run(args.limit, args.with_embeddings))
