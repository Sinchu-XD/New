from pyrogram import filters

from Pronova.Bot import bot, engine
from Pronova.Utils.Font import sc

from Pronova.Utils.Allow import admin_only, check_ban
from Pronova.Utils.Logger import LOGGER


async def safe_vc(action, *args):
    try:
        return await action(*args)
    except Exception as e:
        LOGGER.error(f"VC Error: {e}")
        return None


@bot.on_message(filters.command("skip"))
async def skip(client, m):
    if not await admin_only(client, m):
        return

    await safe_vc(engine.vc.skip, m.chat.id)
    await m.reply(sc("song skipped by") + " " + m.from_user.mention)


@bot.on_message(filters.command(["stop", "end"]))
async def stop(client, m):
    if not await admin_only(client, m):
        return

    await safe_vc(engine.vc.stop, m.chat.id)
    await m.reply(sc("playback ended by") + " " + m.from_user.mention)


@bot.on_message(filters.command("seek"))
async def seek_cmd(client, m):

    if not await admin_only(client, m):
        return

    if len(m.command) < 2:
        return await m.reply("Usage: /seek 1:20 or /seek 90")

    try:
        text = m.command[1]

        if ":" in text:
            parts = [int(x) for x in text.split(":")]
            if len(parts) == 2:
                seconds = parts[0] * 60 + parts[1]
            elif len(parts) == 3:
                seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
            else:
                return await m.reply("Invalid format")
        else:
            seconds = int(text)

    except Exception:
        return await m.reply("Invalid format")

    ok = await safe_vc(engine.vc.seek, m.chat.id, seconds)
    if not ok:
        await m.reply("Seek failed")


@bot.on_message(filters.command("pause"))
async def pause(client, m):
    if not await admin_only(client, m):
        return

    await safe_vc(engine.vc.pause, m.chat.id)
    await m.reply(sc("paused by") + " " + m.from_user.mention)


@bot.on_message(filters.command("resume"))
async def resume(client, m):
    if not await admin_only(client, m):
        return

    await safe_vc(engine.vc.resume, m.chat.id)
    await m.reply(sc("resumed by") + " " + m.from_user.mention)


@bot.on_message(filters.command("previous"))
async def previous(client, m):
    if not await admin_only(client, m):
        return

    ok = await safe_vc(engine.vc.previous, m.chat.id)
    if not ok:
        return await m.reply(sc("no previous song"))

    await m.reply(sc("previous played by") + " " + m.from_user.mention)


@bot.on_message(filters.command("loop"))
async def loop(client, m):
    if not await admin_only(client, m):
        return

    count = None

    if len(m.command) > 1:
        try:
            count = int(m.command[1])
        except Exception:
            return await m.reply(sc("invalid loop value"))

    try:
        result = engine.vc.loop(m.chat.id, count)
    except Exception as e:
        LOGGER.error(f"Loop Error: {e}")
        return await m.reply("Loop failed")

    if count is None:
        status = "enabled" if result else "disabled"
        return await m.reply(sc(f"loop {status}"))

    await m.reply(sc("loop set to") + f" {result}")


@bot.on_message(filters.command("eta"))
async def eta(client, m):

    if await check_ban(m):
        return

    try:
        remaining = engine.vc.eta(m.chat.id)
    except Exception as e:
        LOGGER.error(f"ETA Error: {e}")
        return await m.reply("Error fetching ETA")

    if remaining is None:
        return await m.reply(sc("no active song"))

    await m.reply(sc("remaining time") + f": {remaining}s")


@bot.on_message(filters.command("forward"))
async def forward(client, m):
    if not await admin_only(client, m):
        return

    ok = await safe_vc(engine.vc.seek, m.chat.id, 10)
    if not ok:
        return await m.reply(sc("cannot forward"))

    await m.reply(sc("forwarded 10s"))


@bot.on_message(filters.command("rewind"))
async def rewind(client, m):
    if not await admin_only(client, m):
        return

    ok = await safe_vc(engine.vc.seek, m.chat.id, -10)
    if not ok:
        return await m.reply(sc("cannot rewind"))

    await m.reply(sc("rewinded 10s"))

"""
@bot.on_message(filters.command("volume"))
async def volume(client, m):
    if not await admin_only(client, m):
        return

    if len(m.command) < 2:
        return await m.reply(sc("give volume 0-200"))

    try:
        vol = int(m.command[1])
    except Exception:
        return await m.reply(sc("invalid volume"))

    await safe_vc(engine.vc.volume, m.chat.id, vol)
    await m.reply(sc("volume set to") + f" {vol}")


@bot.on_message(filters.command("mute"))
async def mute(client, m):
    if not await admin_only(client, m):
        return

    await safe_vc(engine.vc.mute, m.chat.id)
    await m.reply(sc("muted by") + " " + m.from_user.mention)


@bot.on_message(filters.command("unmute"))
async def unmute(client, m):
    if not await admin_only(client, m):
        return

    await safe_vc(engine.vc.unmute, m.chat.id)
    await m.reply(sc("unmuted by") + " " + m.from_user.mention)
"""

@bot.on_message(filters.command("queue"))
async def queue(client, m):
    if not await admin_only(client, m):
        return

    try:
        q = engine.vc.player.queues.get(m.chat.id)

        if not q or not getattr(q, "items", None):
            return await m.reply(sc("queue empty"))

        text = sc("queue list") + "\n\n"

        for i, s in enumerate(q.items, 1):
            title = getattr(s, "title", "unknown")
            dur = getattr(s, "duration_sec", 0)
            text += f"{i}. {title} ({dur}s)\n"

        await m.reply(text)

    except Exception as e:
        LOGGER.error(f"Queue Error: {e}")
        await m.reply(sc("unable to fetch queue"))
