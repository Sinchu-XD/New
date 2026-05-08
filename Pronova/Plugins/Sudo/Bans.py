from pyrogram import filters

from Pronova.Bot import bot
from Pronova.Utils.Font import sc

from Pronova.Utils.Allow import admin_only, sudo_only, check_ban
from Pronova.Utils.Logger import LOGGER

from Pronova.Database import (
    ban_user, unban_user,
    gban_user, ungban_user,
    is_banned, is_gbanned,
    get_banned, get_gbanned
)


async def get_target(client, m):
    try:
        if m.reply_to_message and m.reply_to_message.from_user:
            return m.reply_to_message.from_user

        if len(m.command) < 2:
            return None

        target = m.command[1]

        if target.isdigit():
            return await client.get_users(int(target))

        return await client.get_users(target)

    except Exception as e:
        LOGGER.error(f"Get Target Error: {e}")
        return None


def protected(user, owner_id):
    if not user:
        return True
    if user.is_bot:
        return True
    if user.id == owner_id:
        return True
    return False


@bot.on_message(filters.command("bban") & filters.group)
async def ban(client, m):

    if await check_ban(m):
        return

    if not await admin_only(client, m):
        return

    user = await get_target(client, m)
    if not user:
        return await m.reply(sc("reply / give username / user id"))

    if protected(user, client.me.id):
        return await m.reply(sc("cannot ban this user"))

    await ban_user(m.chat.id, user.id)

    await m.reply(f"{sc('user banned from using bot')}\n\n{user.mention}")


@bot.on_message(filters.command("bunban") & filters.group)
async def unban(client, m):

    if await check_ban(m):
        return

    if not await admin_only(client, m):
        return

    user = await get_target(client, m)
    if not user:
        return await m.reply(sc("reply / give username / user id"))

    await unban_user(m.chat.id, user.id)

    await m.reply(f"{sc('user unbanned')}\n\n{user.mention}")


@bot.on_message(filters.command("gban"))
async def gban(client, m):

    if await check_ban(m):
        return

    if not await sudo_only(client, m):
        return

    user = await get_target(client, m)
    if not user:
        return await m.reply(sc("reply / give username / user id"))

    if protected(user, client.me.id):
        return await m.reply(sc("cannot gban this user"))

    await gban_user(user.id)

    await m.reply(f"{sc('user globally banned')}\n\n{user.mention}")


@bot.on_message(filters.command("ungban"))
async def ungban(client, m):

    if await check_ban(m):
        return

    if not await sudo_only(client, m):
        return

    user = await get_target(client, m)
    if not user:
        return await m.reply(sc("reply / give username / user id"))

    await ungban_user(user.id)

    await m.reply(f"{sc('user globally unbanned')}\n\n{user.mention}")


@bot.on_message(filters.command("checkban") & filters.group)
async def checkban(client, m):

    if await check_ban(m):
        return

    if not await admin_only(client, m):
        return

    user = await get_target(client, m)
    if not user:
        return await m.reply(sc("reply / give username / user id"))

    if await is_gbanned(user.id):
        return await m.reply(sc("user is gbanned"))

    if await is_banned(m.chat.id, user.id):
        return await m.reply(sc("user is banned in this chat"))

    await m.reply(sc("user is free"))


@bot.on_message(filters.command("totalbanned") & filters.group)
async def total_banned_cmd(client, m):

    if await check_ban(m):
        return

    if not await admin_only(client, m):
        return

    users = await get_banned(m.chat.id)
    await m.reply(f"{sc('total banned users')} : {len(users)}")


@bot.on_message(filters.command("totalgbanned"))
async def total_gbanned_cmd(client, m):

    if await check_ban(m):
        return

    if not await sudo_only(client, m):
        return

    users = await get_gbanned()
    await m.reply(f"{sc('total gbanned users')} : {len(users)}")
