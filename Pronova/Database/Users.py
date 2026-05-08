from datetime import datetime
from .Core import db
from .Stats import inc_lifetime, inc_daily


def _user_id(user):
    try:
        if isinstance(user, int):
            return int(user)
        if getattr(user, "is_bot", False):
            return None
        return int(user.id)
    except:
        return None


async def add_user(user):
    uid = _user_id(user)
    if not uid:
        return

    now = datetime.utcnow()

    res = await db.users.update_one(
        {"user_id": uid},
        {
            "$setOnInsert": {
                "user_id": uid,
                "join_date": now,
            }
        },
        upsert=True,
    )

    if res.upserted_id:
        await inc_lifetime("users")
        await inc_daily("users")

        await db.users_backup.update_one(
            {"user_id": uid},
            {
                "$setOnInsert": {
                    "user_id": uid,
                    "join_date": now,
                }
            },
            upsert=True,
        )


async def total_users():
    return await db.users.count_documents({})


async def get_users():
    async for u in db.users.find({}, {"user_id": 1, "_id": 0}):
        try:
            yield int(u["user_id"])
        except:
            continue


async def remove_user(user_id):
    try:
        uid = int(user_id)
    except:
        return

    await db.users.delete_one({"user_id": uid})
