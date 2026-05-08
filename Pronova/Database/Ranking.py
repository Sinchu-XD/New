from collections import Counter
from .Core import db


async def top_groups(limit: int = 10):
    result = []

    async for g in db.group_stats.find(
        {},
        {"chat_id": 1, "songs": 1, "_id": 0}
    ).sort("songs", -1).limit(limit):

        try:
            cid = int(g["chat_id"])
            songs = int(g.get("songs", 0))
        except:
            continue

        if songs > 0:
            result.append((cid, songs))

    return result


async def top_users(limit: int = 10):
    counter = Counter()

    async for g in db.group_stats.find(
        {},
        {"users": 1, "_id": 0}
    ):
        users = g.get("users")

        if not isinstance(users, dict):
            continue

        for uid, count in users.items():
            try:
                counter[int(uid)] += int(count)
            except:
                continue

    return counter.most_common(limit)
