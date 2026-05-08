from pyrogram import filters
import time

from Pronova.Bot import bot, engine
from Pronova.Utils.Font import sc
from Pronova.Utils.Allow import admin_only

LAST_ACTION = {}


def can_send(chat_id, cooldown=3):
    now = time.time()
    last = LAST_ACTION.get(chat_id, 0)

    if now - last < cooldown:
        return False

    LAST_ACTION[chat_id] = now
    return True


async def safe_action(action, chat_id, *args):
    try:
        return await action(chat_id, *args)
    except:
        return None


async def safe_reply(m, text):
    if can_send(m.chat.id):
        try:
            await m.reply(text, disable_notification=True)
        except:
            pass


@bot.on_callback_query(filters.regex("^(vc_|seek_|dummy_)"))
async def vc_buttons(_, cq):

    if not cq.message:
        return

    m = cq.message
    chat_id = m.chat.id
    user = cq.from_user
    mention = user.mention

    if not user or user.is_bot:
        return

    if cq.data == "dummy_progress":
        return await cq.answer("⏱ Pʀᴏɢʀᴇss Bᴀʀ", show_alert=False)

    if not await admin_only(bot, cq=cq):
        return

    await cq.answer()

    if cq.data == "vc_skip":
        await safe_action(engine.vc.skip, chat_id)
        await safe_reply(m, sc("song skipped by") + " " + mention)

    elif cq.data == "vc_end":
        if chat_id in engine.vc.player.queues:
            await safe_action(engine.vc.stop, chat_id)
        await safe_reply(m, sc("playback ended by") + " " + mention)

    elif cq.data == "vc_pause":
        await safe_action(engine.vc.pause, chat_id)
        await safe_reply(m, sc("paused by") + " " + mention)

    elif cq.data == "vc_resume":
        await safe_action(engine.vc.resume, chat_id)
        await safe_reply(m, sc("resumed by") + " " + mention)

    elif cq.data == "vc_previous":
        await safe_action(engine.vc.previous, chat_id)
        await safe_reply(m, sc("previous song played by") + " " + mention)

    elif cq.data == "seek_forward":
        try:
            await engine.vc.seek(chat_id, 20)
            
        except AttributeError:
            pass

    elif cq.data == "seek_back":
        try:
            await engine.vc.seek(chat_id, -20)
            
        except AttributeError:
            pass
