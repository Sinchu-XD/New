from .Core import db


async def add_auth(chat_id: int, user_id: int):
    try:
        await db.auth_users.insert_one({
            "chat_id": chat_id,
            "user_id": user_id
        })
        return True
    except:
        return False


async def remove_auth(chat_id: int, user_id: int):
    await db.auth_users.delete_one({
        "chat_id": chat_id,
        "user_id": user_id
    })


async def is_auth(chat_id: int, user_id: int):
    data = await db.auth_users.find_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"_id": 1}
    )
    return data is not None


async def get_auth_users(chat_id: int):
    users = []

    async for user in db.auth_users.find(
        {"chat_id": chat_id},
        {"user_id": 1, "_id": 0}
    ):
        users.append(user["user_id"])

    return users
