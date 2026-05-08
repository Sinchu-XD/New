from pyrogram import filters
from Pronova.Bot import bot
from Pronova.Database import add_auth, remove_auth, get_auth_users
from Pronova.Utils.Font import sc
from Pronova.Utils.Allow import admin_only
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


# ✅ AUTH
@bot.on_message(filters.command("auth") & filters.group)
async def auth(client, message):

    if not await admin_only(client, message):
        return

    user = await resolve_user(client, message)

    if not user:
        return await message.reply(
            sc("reply to a user's message or give username / user id")
        )

    if await add_auth(message.chat.id, user.id):
        await message.reply(f"✓ {user.mention} {sc('authorized')}")
    else:
        await message.reply(f"• {user.mention} {sc('already authorized')}")


# ❌ UNAUTH
@bot.on_message(filters.command("unauth") & filters.group)
async def unauth(client, message):

    if not await admin_only(client, message):
        return

    user = await resolve_user(client, message)

    if not user:
        return await message.reply(
            sc("reply to a user's message or give username / user id")
        )

    await remove_auth(message.chat.id, user.id)
    await message.reply(f"✓ {user.mention} {sc('authorization removed')}")


# 📜 AUTH LIST
@bot.on_message(filters.command("authlist") & filters.group)
async def authlist(client, message):

    if not await admin_only(client, message):
        return

    users = await get_auth_users(message.chat.id)

    if not users:
        return await message.reply(sc("no authorized users"))

    text = f"🔐 {sc('authorized users')}\n\n"

    for uid in users:
        try:
            user = await client.get_users(uid)
            text += f"• {user.mention}\n"
        except Exception:
            text += f"• `{uid}`\n"

    await message.reply(text)
