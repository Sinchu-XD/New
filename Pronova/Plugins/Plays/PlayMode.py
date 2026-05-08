import asyncio
from pyrogram import filters

from Pronova.Bot import bot
from Pronova.Database import *
from Pronova.Utils.Allow import admin_only
from Pronova.Utils.Logger import LOGGER


@bot.on_message(filters.command("adminplay") & filters.group)
async def admin_play(_, m):

    if not m.from_user:
        return

    if not await admin_only(bot, message=m):
        return

    await set_admin_only(m.chat.id, True)

    LOGGER.info(f"[PlayMode] AdminOnly Enabled in {m.chat.id} by {m.from_user.id}")

    await m.reply(
        "🔒 **Admin Play Mode Enabled**\n\n"
        "Now only admins can use play commands."
    )


@bot.on_message(filters.command("allplay") & filters.group)
async def all_play(_, m):

    if not m.from_user:
        return

    if not await admin_only(bot, message=m):
        return

    await set_admin_only(m.chat.id, False)

    LOGGER.info(f"[PlayMode] Everyone Mode Enabled in {m.chat.id} by {m.from_user.id}")

    await m.reply(
        "🌍 **Everyone Play Mode Enabled**\n\n"
        "Now everyone can use play commands."
    )


@bot.on_message(filters.command("playmode") & filters.group)
async def playmode(_, m):

    if not m.from_user:
        return

    try:
        mode = await is_admin_only(m.chat.id)

        if mode:
            text = "🔒 **Play Mode : Admin Only**"
        else:
            text = "🌍 **Play Mode : Everyone**"

        await m.reply(text)

    except Exception as e:
        LOGGER.error(f"[PlayMode Error] {e}")
        await m.reply("❌ Failed to fetch play mode.")
