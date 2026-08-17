"""
👥 Seed sample users into MongoDB Atlas.

Run:  python -m seed.seed_users
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import users_col  # noqa: E402

SAMPLE_USERS = [
    {"name": "Ali Baig", "email": "ali@gmail.com", "role": "admin"},
    {"name": "Maya Patel", "email": "maya.patel@gmail.com", "role": "engineer"},
    {"name": "Jordan Kim", "email": "jordan.kim@gmail.com", "role": "engineer"},
]


async def run():
    for u in SAMPLE_USERS:
        existing = await users_col.find_one({"email": u["email"]})
        if existing:
            print(f"↷ Skipping existing user {u['email']}")
            continue
        await users_col.insert_one({**u, "createdAt": datetime.utcnow()})
        print(f"✅ Created user {u['email']} ({u['role']})")

    print("\n🎉 User seeding complete. Use any of these emails to log in via OTP:")
    for u in SAMPLE_USERS:
        print(f"   - {u['email']}  ({u['role']})")


if __name__ == "__main__":
    asyncio.run(run())
