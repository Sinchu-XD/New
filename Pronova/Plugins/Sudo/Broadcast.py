import asyncio
import time

from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid

from Pronova.Bot import bot
from Pronova.Utils.Font import sc

from Pronova.Utils.Allow import sudo_only, check_ban
from Pronova.Utils.Logger import LOGGER

from Pronova.Database import get_users, remove_user
from Pronova.Database import get_all_chats
from Pronova.Database import inc_lifetime
from Pronova.Database import db


DELAY = 0.25
PROGRESS_EVERY = 200


async def send_and_pin(target_id, msg):
    try:
        sent = await bot.forward_messages(target_id, msg.chat.id, msg.id)

        try:
            await bot.pin_chat_message(target_id, sent.id)
        except Exception:
            pass

        return True

    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        try:
            sent = await bot.forward_messages(target_id, msg.chat.id, msg.id)

            try:
                await bot.pin_chat_message(target_id, sent.id)
            except Exception:
                pass

            return True
        except Exception:
            return False

    except (UserIsBlocked, PeerIdInvalid):
        try:
            await remove_user(target_id)
        except Exception:
            pass
        return False

    except Exception as e:
        LOGGER.error(f"Broadcast Error ({target_id}): {e}")
        return False


@bot.on_message(filters.command("broadcast"))
async def broadcast(client, message):

    if await check_ban(message):
        return

    if not await sudo_only(client, message):
        return

    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast.")

    start_time = time.time()
    msg = message.reply_to_message

    total = 0
    success = 0
    failed = 0

    status = await message.reply(sc("broadcast started..."))

    async for user_id in get_users():
        uid = int(user_id)
        total += 1

        ok = await send_and_pin(uid, msg)

        if ok:
            success += 1
        else:
            failed += 1

        await asyncio.sleep(DELAY)

        if total % PROGRESS_EVERY == 0:
            try:
                await status.edit(
                    f"{sc('broadcasting')}\n\n{sc('processed')} : {total}"
                )
            except Exception:
                pass

    async for chat_id in get_all_chats():
        cid = int(chat_id)
        total += 1

        ok = await send_and_pin(cid, msg)

        if ok:
            success += 1
        else:
            failed += 1

        await asyncio.sleep(DELAY)

        if total % PROGRESS_EVERY == 0:
            try:
                await status.edit(
                    f"{sc('broadcasting')}\n\n{sc('processed')} : {total}"
                )
            except Exception:
                pass

    try:
        await db.broadcasts.insert_one({
            "total": total,
            "success": success,
            "failed": failed,
            "time": int(time.time())
        })
    except Exception as e:
        LOGGER.error(f"Broadcast Log Error: {e}")

    await inc_lifetime("broadcasts")

    taken = round(time.time() - start_time, 2)

    final = (
        f"✅ {sc('broadcast completed')}\n\n"
        f"{sc('total targets')} : {total}\n"
        f"{sc('success')} : {success}\n"
        f"{sc('failed')} : {failed}\n\n"
        f"{sc('time taken')} : {taken}s"
    )

    try:
        await status.edit(final)
    except Exception:
        pass
