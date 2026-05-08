from .Core import db
from .Stats import inc_lifetime


def _to_int(x):
    try:
        return int(x.id) if hasattr(x, "id") else int(x)
    except:
        return None


async def _exists(collection, query):
    data = await collection.find_one(query, {"_id": 1})
    return data is not None


async def _get_list(collection, query, field):
    result = []
    async for x in collection.find(query, {field: 1, "_id": 0}):
        try:
            result.append(int(x[field]))
        except:
            continue
    return result


async def ban_user(chat, user):
    cid = _to_int(chat)
    uid = _to_int(user)
    if not cid or not uid:
        return

    res = await db.banned.update_one(
        {"chat_id": cid, "user_id": uid},
        {"$setOnInsert": {"chat_id": cid, "user_id": uid}},
        upsert=True,
    )

    if res.upserted_id:
        await inc_lifetime("banned")


async def unban_user(chat, user):
    cid = _to_int(chat)
    uid = _to_int(user)
    if not cid or not uid:
        return

    await db.banned.delete_one({"chat_id": cid, "user_id": uid})


async def is_banned(chat, user):
    cid = _to_int(chat)
    uid = _to_int(user)
    if not cid or not uid:
        return False

    return await _exists(db.banned, {"chat_id": cid, "user_id": uid})


async def get_banned(chat):
    cid = _to_int(chat)
    if not cid:
        return []

    return await _get_list(db.banned, {"chat_id": cid}, "user_id")


async def total_banned():
    return await db.banned.count_documents({})


async def gban_user(user):
    uid = _to_int(user)
    if not uid:
        return

    res = await db.gbanned.update_one(
        {"user_id": uid},
        {"$setOnInsert": {"user_id": uid}},
        upsert=True,
    )

    if res.upserted_id:
        await inc_lifetime("gbanned")


async def ungban_user(user):
    uid = _to_int(user)
    if not uid:
        return

    await db.gbanned.delete_one({"user_id": uid})


async def is_gbanned(user):
    uid = _to_int(user)
    if not uid:
        return False

    return await _exists(db.gbanned, {"user_id": uid})


async def get_gbanned():
    return await _get_list(db.gbanned, {}, "user_id")
