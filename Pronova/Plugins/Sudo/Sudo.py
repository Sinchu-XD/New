from pyrogram import filters

from Pronova.Bot import bot
from Pronova.Database import add_sudo, remove_sudo, get_all_sudo
from Pronova.Utils.Font import sc

from Pronova.Utils.Allow import check_ban, owner_only
from Pronova.Utils.Logger import LOGGER


async def resolve_user(client, message):
    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user

        if len(message.command) < 2:
            return None

        target = message.command[1]

        if target.isdigit():
            return await client.get_users(int(target))

        return await client.get_users(target)

    except Exception as e:
        LOGGER.error(f"Resolve User Error: {e}")
        return None


@bot.on_message(filters.command("addsudo"))
async def addsudo(client, message):

    if await check_ban(message):
        return

    if not await owner_only(client, message):
        return

    user = await resolve_user(client, message)

    if not user:
        return await message.reply(
            sc("reply / give username / user id")
        )

    if user.is_bot:
        return await message.reply(sc("cannot add bot as sudo"))

    if user.id == client.me.id:
        return await message.reply(sc("cannot add bot itself"))

    if await add_sudo(user.id):
        await message.reply(f"✓ {user.mention} {sc('added to sudo')}")
    else:
        await message.reply(f"• {user.mention} {sc('already sudo')}")


@bot.on_message(filters.command("delsudo"))
async def delsudo(client, message):

    if await check_ban(message):
        return

    if not await owner_only(client, message):
        return

    user = await resolve_user(client, message)

    if not user:
        return await message.reply(
            sc("reply / give username / user id")
        )

    await remove_sudo(user.id)
    await message.reply(f"✓ {user.mention} {sc('removed from sudo')}")


@bot.on_message(filters.command("sudolist"))
async def sudolist(client, message):

    if await check_ban(message):
        return

    if not await owner_only(client, message):
        return

    users = await get_all_sudo()

    if not users:
        return await message.reply(sc("no sudo users"))

    text = f"👑 {sc('sudo users')}\n\n"

    try:
        user_objs = await client.get_users(users)
        for user in user_objs:
            text += f"• {user.mention}\n"
    except Exception as e:
        LOGGER.error(f"SudoList Bulk Fetch Error: {e}")
        for uid in users:
            text += f"• `{uid}`\n"

    await message.reply(text)
