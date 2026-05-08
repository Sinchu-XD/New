import asyncio

from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    PeerIdInvalid,
    UserBannedInChannel,
    UserNotParticipant,
    ChannelPrivate
)

from Pronova.Bot import bot, user
from Pronova.Utils.Font import sc
from Pronova.Utils.Logger import LOGGER


ASSISTANT_ID = None
ASSISTANT_USERNAME = None

JOINING = set()
LOCK = asyncio.Lock()


async def setup_assistant():
    global ASSISTANT_ID, ASSISTANT_USERNAME

    async with LOCK:
        if ASSISTANT_ID:
            return

        me = await user.get_me()
        ASSISTANT_ID = me.id
        ASSISTANT_USERNAME = me.username


async def is_assistant_in_chat(chat_id):
    try:
        chat = await user.get_chat(chat_id)
        member = await user.get_chat_member(chat.id, ASSISTANT_ID)

        return member.status not in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED
        )

    except (UserNotParticipant, UserBannedInChannel, ChannelPrivate):
        return False

    except Exception as e:
        LOGGER.error(f"[Assistant Check Error] {e}")
        return False


async def get_ass(chat_id, m=None):
    global ASSISTANT_ID, ASSISTANT_USERNAME

    if not ASSISTANT_ID:
        await setup_assistant()

    try:
        chat = await bot.get_chat(chat_id)

        if chat.type not in (ChatType.SUPERGROUP, ChatType.CHANNEL):
            if m:
                await m.reply("❌ This command only works in groups/channels.")
            return False

        chat_id = chat.id

    except Exception as e:
        LOGGER.error(f"[Chat Validation Error] {e}")
        return False

    if await is_assistant_in_chat(chat_id):
        return True

    if chat_id in JOINING:
        return False

    JOINING.add(chat_id)

    try:
        bot_me = await bot.get_me()

        try:
            bot_member = await bot.get_chat_member(chat_id, bot_me.id)
        except ChatAdminRequired:
            if m:
                await m.reply("⚠️ Bot must be admin with invite permission.")
            return False

        if not bot_member.privileges or not bot_member.privileges.can_invite_users:
            if m:
                await m.reply("⚠️ Bot needs invite users permission.")
            return False

        try:
            link = await bot.export_chat_invite_link(chat_id)
            await user.join_chat(link)
            await asyncio.sleep(2)

        except UserAlreadyParticipant:
            pass

        except Exception as e:
            LOGGER.error(f"[Join Failed] {e}")

        if await is_assistant_in_chat(chat_id):
            return True

        if not (bot_member.privileges and bot_member.privileges.can_restrict_members):
            if m:
                username = f"@{ASSISTANT_USERNAME}" if ASSISTANT_USERNAME else f"`{ASSISTANT_ID}`"

                await m.reply(
                    sc(
                        "Assistant is banned in this group.\n"
                        "Bot can't unban it.\n"
                        f"Unban manually: /unban {ASSISTANT_ID} or {username}"
                    )
                )
            return False

        try:
            await bot.unban_chat_member(chat_id, ASSISTANT_ID)
            await asyncio.sleep(2)
        except Exception as e:
            LOGGER.error(f"[Unban Error] {e}")

        try:
            link = await bot.export_chat_invite_link(chat_id)
            await user.join_chat(link)
            await asyncio.sleep(3)
        except Exception as e:
            LOGGER.error(f"[Join After Unban Error] {e}")

        if await is_assistant_in_chat(chat_id):
            return True

        if m:
            await m.reply("❌ Assistant could not join. Add manually.")

        return False

    except (ChatAdminRequired, PeerIdInvalid):
        if m:
            username = f"@{ASSISTANT_USERNAME}" if ASSISTANT_USERNAME else f"`{ASSISTANT_ID}`"

            await m.reply(
                sc(
                    "Assistant is not in the chat.\n"
                    "Give invite permission or add manually."
                )
                + f"\n\n{username}\n`{ASSISTANT_ID}`"
            )
        return False

    except Exception as e:
        LOGGER.error(f"[Assistant Join Error] {e}")

        if m:
            await m.reply(sc("❌ Failed to bring assistant."))

        return False

    finally:
        JOINING.discard(chat_id)
