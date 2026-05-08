from datetime import datetime
from .Core import db
from .Stats import inc_lifetime, inc_daily


def _chat_id(chat):
    try:
        return int(chat.id) if hasattr(chat, "id") else int(chat)
    except:
        return None


async def add_chat(chat):
    cid = _chat_id(chat)
    if not cid:
        return

    res = await db.chats.update_one(
        {"chat_id": cid},
        {
            "$setOnInsert": {
                "chat_id": cid,
                "join_date": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    if res.upserted_id:
        await inc_lifetime("chats")
        await inc_daily("chats")


async def total_chats():
    return await db.chats.count_documents({})


async def get_all_chats():
    async for c in db.chats.find({}, {"chat_id": 1, "_id": 0}):
        try:
            yield int(c["chat_id"])
        except:
            continue
