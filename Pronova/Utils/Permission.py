from pyrogram.enums import ChatMemberStatus
from Pronova.Database import is_sudo, is_auth
from Config import *
from datetime import datetime, time
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")

NIGHT_START = time(23, 30)
NIGHT_END = time(8, 0)


def is_night_time():
    now = datetime.now(IST).time()
    return now >= NIGHT_START or now <= NIGHT_END


async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False


async def is_allowed(client, message, notify=False):
    if not message.from_user:
        return False

    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id == OWNER_ID:
        return True

    if await is_sudo(user_id):
        return True

    if await is_admin(client, chat_id, user_id):
        return True

    if await is_auth(chat_id, user_id):
        return True

    if is_night_time():
        if notify:
            await message.reply(
                
                    "**Play disabled at night for non-admin users**\n\n"
                    "Ask an admin to allow you using /auth\n"
                    "Or wait till morning (8 AM)"
                )
            
        return False

    return True
