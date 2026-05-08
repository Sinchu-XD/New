from .Core import db


async def add_sudo(user_id: int):
    try:
        await db.sudo_users.insert_one({"user_id": int(user_id)})
        return True
    except:
        return False


async def remove_sudo(user_id: int):
    await db.sudo_users.delete_one({"user_id": int(user_id)})


async def is_sudo(user_id: int):
    data = await db.sudo_users.find_one(
        {"user_id": int(user_id)},
        {"_id": 1}
    )
    return data is not None


async def get_all_sudo():
    users = []

    async for user in db.sudo_users.find(
        {},
        {"user_id": 1, "_id": 0}
    ):
        try:
            users.append(int(user["user_id"]))
        except:
            continue

    return users
