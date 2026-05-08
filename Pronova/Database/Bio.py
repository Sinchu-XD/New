from .Core import db
import time


async def add_verified(user_id: int):
    await db.verified_users.update_one(
        {"_id": user_id},
        {"$set": {"_id": user_id}},
        upsert=True
    )


async def is_verified(user_id: int):
    return await db.verified_users.find_one({"_id": user_id}) is not None


async def remove_verified(user_id: int):
    await db.verified_users.delete_one({"_id": user_id})


async def add_warn(chat_id: int, user_id: int):
    key = f"{chat_id}:{user_id}"
    now = int(time.time())

    data = await db.warns.find_one({"_id": key})

    if not data:
        await db.warns.insert_one({
            "_id": key,
            "count": 1,
            "time": now
        })
        return 1

    count = data.get("count", 0) + 1

    await db.warns.update_one(
        {"_id": key},
        {"$set": {"count": count, "time": now}}
    )

    return count


async def get_warn(chat_id: int, user_id: int):
    data = await db.warns.find_one({"_id": f"{chat_id}:{user_id}"})
    return data.get("count", 0) if data else 0


async def reset_warn(chat_id: int, user_id: int):
    await db.warns.delete_one({"_id": f"{chat_id}:{user_id}"})


async def set_bio_cache(user_id: int, bio: str):
    await db.bio_cache.update_one(
        {"_id": user_id},
        {"$set": {
            "bio": bio,
            "time": int(time.time())
        }},
        upsert=True
    )


async def get_bio_cache(user_id: int, ttl=3600):
    data = await db.bio_cache.find_one({"_id": user_id})

    if not data:
        return None

    if int(time.time()) - data.get("time", 0) > ttl:
        return None

    return data.get("bio")
