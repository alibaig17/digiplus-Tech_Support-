"""
🗄️ MongoDB Atlas connection (async, via Motor).
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.mongodb_db_name]

# Collections
users_col = db["users"]
tickets_col = db["tickets"]
kb_col = db["knowledge_base"]
otp_col = db["otp_codes"]
chats_col = db["ticket_chats"]
resolutions_col = db["ticket_resolutions"]
analytics_col = db["analytics"]


async def ensure_indexes():
    """📇 Create indexes needed for fast lookups & text search."""
    await users_col.create_index("email", unique=True)
    await otp_col.create_index("email")
    await otp_col.create_index("expires_at", expireAfterSeconds=0)
    await tickets_col.create_index([("title", "text"), ("description", "text"), ("category", "text")])
    await tickets_col.create_index("status")
    await tickets_col.create_index("priority")
    await kb_col.create_index([("title", "text"), ("content", "text"), ("tags", "text")])
    await chats_col.create_index("ticket_id")
    await resolutions_col.create_index("ticket_id")
