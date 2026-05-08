from datetime import datetime, timedelta
from .Core import db


def today():
    return datetime.utcnow().strftime("%d-%m-%Y")


async def inc_lifetime(key: str):
    if not key:
        return

    await db.lifetime.update_one(
        {"_id": str(key)},
        {"$inc": {"count": 1}},
        upsert=True,
    )


async def get_lifetime(key: str) -> int:
    if not key:
        return 0

    data = await db.lifetime.find_one(
        {"_id": str(key)},
        {"count": 1, "_id": 0}
    )

    if not data:
        return 0

    try:
        return int(data["count"])
    except:
        return 0


async def inc_daily(key: str):
    if not key:
        return

    await db.daily.update_one(
        {"date": today()},
        {"$inc": {str(key): 1}},
        upsert=True,
    )


async def sum_range(days: int, key: str) -> int:
    if not key or days <= 0:
        return 0

    now = datetime.utcnow()

    dates = [
        (now - timedelta(days=i)).strftime("%d-%m-%Y")
        for i in range(days)
    ]

    total = 0

    async for data in db.daily.find(
        {"date": {"$in": dates}},
        {key: 1, "_id": 0}
    ):
        try:
            total += int(data.get(key, 0))
        except:
            continue

    return total
