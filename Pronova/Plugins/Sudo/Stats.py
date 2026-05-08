from pyrogram import filters

from Pronova.Bot import bot
from Pronova.Utils.Font import sc

from Pronova.Utils.Allow import sudo_only, check_ban
from Pronova.Utils.Logger import LOGGER

from Pronova.Database import *


USER_CACHE = {}
CHAT_CACHE = {}


@bot.on_message(filters.command("stats"))
async def stats(client, m):

    if not m.from_user:
        return

    if await check_ban(m):
        return

    if not await sudo_only(client, m):
        return

    msg = await m.reply(sc("fetching analytics..."))

    try:
        users = await total_users()
        chats = await total_chats()
        songs = await get_lifetime("songs")
        commands = await get_lifetime("commands")

        banned = await total_banned()
        gbanned = await db.gbanned.count_documents({})

        weekly_users = await sum_range(7, "users")
        monthly_users = await sum_range(30, "users")

        tg = await top_groups(3)
        tu = await top_song_players(3)
        mp = await most_played(3)

        total_sudo = await db.sudo_users.count_documents({})
        total_auth = await db.auth_users.count_documents({})

    except Exception as e:
        LOGGER.error(f"Stats Fetch Error: {e}")
        return await msg.edit(sc("failed to fetch stats"))

    text = f"📊 {sc('bot analytics')}\n\n"

    text += f"{sc('users')} : {users}\n"
    text += f"{sc('chats')} : {chats}\n"
    text += f"{sc('songs')} : {songs}\n"
    text += f"{sc('commands')} : {commands}\n\n"

    text += f"{sc('sudo users')} : {total_sudo}\n"
    text += f"{sc('auth users')} : {total_auth}\n\n"

    text += f"{sc('banned (groups)')} : {banned}\n"
    text += f"{sc('gbanned (global)')} : {gbanned}\n\n"

    text += f"📈 {sc('growth')}\n"
    text += f"7 {sc('days')} : {weekly_users}\n"
    text += f"30 {sc('days')} : {monthly_users}\n\n"

    text += f"🏆 {sc('top groups')}\n"

    if tg:
        for i, (cid, s) in enumerate(tg, 1):
            try:
                cid = int(cid)

                if cid in CHAT_CACHE:
                    name = CHAT_CACHE[cid]
                else:
                    chat = await client.get_chat(cid)
                    name = chat.title
                    CHAT_CACHE[cid] = name

            except Exception:
                name = cid

            text += f"{i}. {name} → {s}\n"
    else:
        text += f"{sc('no data')}\n"

    text += f"\n👤 {sc('top users')}\n"

    if tu:
        for i, (uid, c) in enumerate(tu, 1):
            try:
                uid = int(uid)

                if uid in USER_CACHE:
                    mention = USER_CACHE[uid]
                else:
                    user = await client.get_users(uid)
                    mention = user.mention
                    USER_CACHE[uid] = mention

            except Exception:
                mention = uid

            text += f"{i}. {mention} → {c}\n"
    else:
        text += f"{sc('no data')}\n"

    text += f"\n🎧 {sc('most played')}\n"

    if mp:
        for i, (name, c) in enumerate(mp, 1):
            text += f"{i}. {name} → {c}\n"
    else:
        text += f"{sc('no data')}\n"

    try:
        await msg.edit(text)
    except Exception as e:
        LOGGER.error(f"Stats Edit Error: {e}")
