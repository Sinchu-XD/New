import re
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import ChatPermissions
from pyrogram.raw.functions.users import GetFullUser

from Pronova.Bot import bot

from Pronova.Utils.Allow import admin_only, check_ban
from Pronova.Utils.Logger import LOGGER

from Pronova.Database import (
    add_verified,
    is_verified,
    add_warn,
    get_bio_cache,
    set_bio_cache
)


LINK_REGEX = r"(https?://\S+|t\.me/\S+|@\w+)"
MAX_GC_MEMBERS = 100
MAX_WARNS = 3


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


@bot.on_message(filters.command("verify") & filters.group)
async def verify_user(client, message):

    if await check_ban(message):
        return

    if not await admin_only(client, message):
        return

    user = await resolve_user(client, message)

    if not user:
        return await message.reply("Reply / give username / user id")

    await add_verified(user.id)

    username = f"@{user.username}" if user.username else "No Username"

    msg = await message.reply(
        f"""✅ User Verified

👤 Name : {user.mention}
🆔 User ID : `{user.id}`
🔗 Username : {username}

Bio link filter disabled."""
    )

    await asyncio.sleep(30)
    try:
        await msg.delete()
    except:
        pass


@bot.on_message(filters.group & filters.incoming)
async def bio_link_checker(client, message):

    if not message.from_user:
        return

    if await check_ban(message):
        return

    chat = message.chat
    user_id = message.from_user.id

    if await is_verified(user_id):
        return

    if chat.type == ChatType.GROUP:
        try:
            members = await client.get_chat_members_count(chat.id)
            if members <= MAX_GC_MEMBERS:
                return
        except:
            return

    try:
        member = await client.get_chat_member(chat.id, user_id)
        if member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ):
            return
    except:
        return

    try:
        bio = await get_bio_cache(user_id)

        if not bio:
            full = await client.invoke(
                GetFullUser(id=await client.resolve_peer(user_id))
            )
            bio = full.full_user.about

            if bio:
                await set_bio_cache(user_id, bio)

        if not bio:
            return

        if re.search(LINK_REGEX, bio):

            try:
                await message.delete()
            except:
                pass

            warn_count = await add_warn(chat.id, user_id)

            if warn_count >= MAX_WARNS:

                try:
                    await client.restrict_chat_member(
                        chat.id,
                        user_id,
                        ChatPermissions()
                    )
                except Exception as e:
                    LOGGER.error(f"Mute Error: {e}")

                msg = await message.reply(
                    f"""🔇 User Muted

User : {message.from_user.mention}
Reason : Bio link spam
Warns : {warn_count}/{MAX_WARNS}"""
                )

            else:

                msg = await message.reply(
                    f"""⚠️ Bio Link Detected

User : {message.from_user.mention}
Warn : {warn_count}/{MAX_WARNS}

Remove link from bio."""
                )

            await asyncio.sleep(30)
            try:
                await msg.delete()
            except:
                pass

    except Exception as e:
        LOGGER.error(f"Bio Checker Error: {e}")
