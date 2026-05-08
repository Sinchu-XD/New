from .Core import db
from .Stats import inc_lifetime, inc_daily
from Pronova.Utils.Logger import LOGGER
from collections import Counter


def normalize_title(title: str) -> str:
    if not title:
        return ""
    return str(title).strip().lower()


def _to_int(x):
    try:
        return int(x.id) if hasattr(x, "id") else int(x)
    except:
        return None


async def inc_song_play(chat=None, user=None, title=None):
    await inc_lifetime("songs")
    await inc_daily("songs")

    cid = _to_int(chat)
    uid = _to_int(user)


    if cid:
        update_data = {
            "$inc": {
                "songs": 1,  # total songs in chat
            }
        }

        if uid:
            update_data["$inc"][f"users.{uid}"] = 1 

        await db.group_stats.update_one(
            {"chat_id": cid},
            update_data,
            upsert=True,
        )


    title = normalize_title(title)
    if not title:
        return

    await db.songs_stats.update_one(
        {"title": title},
        {"$inc": {"played": 1}},
        upsert=True,
    )

    LOGGER.debug(f"Song tracked → chat={cid}, user={uid}, title={title}")

async def top_song_players(limit: int = 5):
    counter = Counter()

    async for g in db.group_stats.find({}, {"users": 1}):

        users = g.get("users")

        if not isinstance(users, dict):
            continue

        for uid, count in users.items():
            try:
                counter[int(uid)] += int(count)
            except:
                continue

    result = counter.most_common(limit)

    LOGGER.info(f"Top song players: {result}")
    return result

async def most_played(limit: int = 10):
    result = []

    async for s in db.songs_stats.find(
        {},
        {"title": 1, "played": 1, "_id": 0}
    ).sort("played", -1).limit(limit):

        try:
            title = s["title"]
            played = int(s.get("played", 0))
        except:
            continue

        if played > 0:
            result.append((title, played))

    return result
