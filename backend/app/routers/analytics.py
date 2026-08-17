"""
📊 Analytics dashboard endpoints — counts, breakdowns, and most-common issues.
"""
from fastapi import APIRouter, Depends
from app.database import tickets_col
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def overview(user: dict = Depends(get_current_user)):
    total = await tickets_col.count_documents({})
    open_count = await tickets_col.count_documents({"status": "Open"})
    in_progress = await tickets_col.count_documents({"status": "In Progress"})
    resolved = await tickets_col.count_documents({"status": "Resolved"})
    critical = await tickets_col.count_documents({"priority": "Critical"})

    async def group_counts(field: str) -> dict:
        pipeline = [{"$group": {"_id": f"${field}", "count": {"$sum": 1}}}]
        out = {}
        async for row in tickets_col.aggregate(pipeline):
            out[row["_id"] or "Unknown"] = row["count"]
        return out

    by_status = await group_counts("status")
    by_category = await group_counts("category")
    by_priority = await group_counts("priority")

    common_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
    ]
    most_common = [
        {"issue": row["_id"] or "Unknown", "count": row["count"]}
        async for row in tickets_col.aggregate(common_pipeline)
    ]

    return {
        "total_tickets": total,
        "open_tickets": open_count,
        "in_progress_tickets": in_progress,
        "resolved_tickets": resolved,
        "critical_tickets": critical,
        "by_status": by_status,
        "by_category": by_category,
        "by_priority": by_priority,
        "most_common_issues": most_common,
    }
