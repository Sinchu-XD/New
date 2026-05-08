from .Core import db


async def set_admin_only(chat_id: int, value: bool):
    await db.play_mode.update_one(
        {"chat_id": chat_id},
        {"$set": {"admin_only": value}},
        upsert=True
    )


async def is_admin_only(chat_id: int):
    data = await db.play_mode.find_one({"chat_id": chat_id})
    if not data:
        return False
    return data.get("admin_only", False)
