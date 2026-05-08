import os
from motor.motor_asyncio import AsyncIOMotorClient
from Config import MONGO_URL


DB_NAME = os.getenv("DB_NAME", "Pronova")


client = AsyncIOMotorClient(
    MONGO_URL,
    maxPoolSize=100,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
)

db = client[DB_NAME]


async def setup_database():
    try:
        await client.admin.command("ping")
        print("MongoDB Connected")
    except Exception as e:
        print("MongoDB Connection Failed:", e)
        return

    indexes = [
        (db.users, "user_id", True),
        (db.users_backup, "user_id", True),

        (db.chats, "chat_id", True),
        (db.group_stats, "chat_id", True),
        (db.songs_stats, "title", True),
 #       (db.group_stats, "chat_id", True),

        (db.gbanned, "user_id", True),
        (db.daily, "date", True),
        (db.gc_activity, "chat_id", True),
        (db.afk, "user_id", True),
        (db.play_mode, "chat_id", True),

        (db.sudo_users, "user_id", True),
        (db.yt_stream_cache, "_id", True),
        (db.yt_search_cache, "_id", True),

        (db.verified_users, "_id", True),
        (db.warns, "_id", True),
        (db.bio_cache, "_id", True),
    ]

    try:
        for collection, field, unique in indexes:
            try:
                await collection.create_index(field, unique=unique)
            except Exception:
                pass

        await db.banned.create_index(
            [("chat_id", 1), ("user_id", 1)],
            unique=True
        )

        await db.auth_users.create_index(
            [("chat_id", 1), ("user_id", 1)],
            unique=True
        )

        await db.warns.create_index(
            "time",
            expireAfterSeconds=86400
        )

        await db.bio_cache.create_index(
            "time",
            expireAfterSeconds=3600
        )

        await db.group_stats.create_index(
            [("chat_id", 1), ("songs", 1)]
        )

        print("MongoDB Indexes Ready")

    except Exception as e:
        print("Index Creation Error:", e)
