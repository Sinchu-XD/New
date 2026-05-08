from Pronova.Utils.Logger import LOGGER

import asyncio
import random
import re

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from pyrogram import enums
from pyrogram.enums import ButtonStyle
from pyrogram.errors import FloodWait

from Pronova.Utils.Thumbnail import get_thumb
from Pronova.Utils._thumb import Thumbnail

thumb = Thumbnail()
generate = thumb.generate


def clean_html(text: str):
    return re.sub(r"<.*?>", "", text)


CUSTOM_EMOJI_IDS = [
    6089195853908548095,
    6334453153823459140,
    6334525760245597578,
    6334832949191509666,
    6334540251465254516,
    6334555537253860831,
    6332440708242212451,
    6097980951814475221,
    6334719188392740438,
    6269122341859495184,
    6271346172846149465,
    6271719066201755333,
    6217467341421154237,
    6237977283433338540,
    6235677650568878393,
    6113826782681502268,
    6116320024081731477
]


def utf16_len(text: str):
    return len(text.encode("utf-16-le")) // 2


def time_to_sec(time_str: str) -> int:
    try:
        parts = [int(p) for p in time_str.split(":")]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return 0
    except:
        return 0


def format_time(seconds: int) -> str:
    if seconds < 0: 
        seconds = 0
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def get_progress_bar(current, total, length=10):
    if total <= 0:
        return "🔘▬▬▬▬▬▬▬▬▬"
    percentage = current / total
    filled = int(length * percentage)
    if filled >= length:
        return "▬▬▬▬▬▬▬▬▬🔘"
    return "▬" * filled + "🔘" + "▬" * (length - filled - 1)


def build_caption(title, url, duration, requester, header="Nᴏᴡ Pʟᴀʏɪɴɢ", position=None):
    try:
        title = title[:30]

        if hasattr(requester, "id"):
            user_id = requester.id
            name = clean_html(requester.first_name)
        else:
            user_id = None
            name = clean_html(str(requester))

        text = (
            f"▫ {header} ▫\n\n"
            f"▫ Tɪᴛʟᴇ : {title} ▫\n\n"
            f"▫ Dᴜʀᴀᴛɪᴏɴ : {duration} ▫\n\n"
            f"▫ Rᴇǫᴜᴇsᴛᴇᴅ Bʏ : {name} ▫"
        )

        if position:
            text += f"\n\n▫ Pᴏsɪᴛɪᴏɴ : {position} ▫"

        full = text
        entities = []

        for i, char in enumerate(full):
            if char == "▫":
                entities.append(
                    MessageEntity(
                        type=enums.MessageEntityType.CUSTOM_EMOJI,
                        offset=utf16_len(full[:i]),
                        length=1,
                        custom_emoji_id=random.choice(CUSTOM_EMOJI_IDS)
                    )
                )

        title_pos = full.find(title)
        if title_pos != -1 and url:
            entities.append(
                MessageEntity(
                    type=enums.MessageEntityType.TEXT_LINK,
                    offset=utf16_len(full[:title_pos]),
                    length=utf16_len(title),
                    url=url
                )
            )

        if user_id:
            name_pos = full.find(name)
            if name_pos != -1:
                entities.append(
                    MessageEntity(
                        type=enums.MessageEntityType.TEXT_LINK,
                        offset=utf16_len(full[:name_pos]),
                        length=utf16_len(name),
                        url=f"tg://user?id={user_id}"
                    )
                )

        return full, entities

    except Exception as e:
        LOGGER.error(f"Error in build_caption: {e}", exc_info=True)
        return "Error generating caption", []


QUEUE_DELETE_AFTER = 30
VC_END_DELETE_AFTER = 10


def control_buttons(progress_text="00:00 ▬▬▬▬▬▬▬▬▬▬ 00:00"):
    try:
        buttons = [
            [InlineKeyboardButton(progress_text, callback_data="dummy_progress", style=ButtonStyle.PRIMARY)],
            [
                InlineKeyboardButton("▷", callback_data="vc_resume", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("II", callback_data="vc_pause", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("I◂◂", callback_data="vc_previous", style=ButtonStyle.DANGER),
                InlineKeyboardButton("‣‣I", callback_data="vc_skip", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("▢", callback_data="vc_end", style=ButtonStyle.SUCCESS),
            ],
            [
                InlineKeyboardButton("⋖ - 𝟤𝟢 ꜱ", callback_data="seek_back", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/WtfShia", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("𝟤𝟢 ꜱ + ⋗", callback_data="seek_forward", style=ButtonStyle.DANGER),
            ],
            [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url="https://t.me/PronovaSupport", style=ButtonStyle.DANGER),
                InlineKeyboardButton("Uᴘᴅᴀᴛᴇꜱ", url="https://t.me/ProNovaUpdates", style=ButtonStyle.PRIMARY)
            ]
        ]

        return InlineKeyboardMarkup(buttons)

    except Exception as e:
        LOGGER.error(f"Error in control_buttons: {e}", exc_info=True)
        return InlineKeyboardMarkup([])


class Plugin:
    name = "base"

    def __init__(self, app):
        self.app = app
        self.now_playing_msg = {}
        self.progress_tasks = {}

    async def progress_loop(self, chat_id, msg, duration_sec):
        try:
            from Pronova.Bot import engine
            while True:
                await asyncio.sleep(15)
                
                current_time = engine.vc.player.current_time(chat_id)

                if current_time >= duration_sec or current_time <= 0:
                    break

                bar = get_progress_bar(current_time, duration_sec)
                time_str = f"{format_time(current_time)} {bar} {format_time(duration_sec)}"
                
                try:
                    await msg.edit_reply_markup(reply_markup=control_buttons(time_str))
                except FloodWait as e:
                    await asyncio.sleep(e.value + 1)
                except Exception:
                    pass
                    
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    async def on_song_start(self, chat_id, song):
        LOGGER.info(f"Song started in {chat_id}: {song.title}")

        caption, entities = build_caption(
            song.title,
            song.url,
            song.duration_text,
            song.requested_by
        )

        old = self.now_playing_msg.get(chat_id)
        if old:
            try:
                await old.delete()
            except Exception:
                pass

        old_task = self.progress_tasks.get(chat_id)
        if old_task:
            old_task.cancel()

        duration_sec = time_to_sec(song.duration_text)
        initial_bar = f"00:00 🔘▬▬▬▬▬▬▬▬▬ {format_time(duration_sec)}" if duration_sec > 0 else "00:00 ▬▬▬▬▬▬▬▬▬▬ 00:00"

        try:
            thumb = await generate(song)

            msg = await self.app.send_photo(
                chat_id,
                photo=thumb,
                caption=caption,
                caption_entities=entities,
                reply_markup=control_buttons(initial_bar)
            )

            self.now_playing_msg[chat_id] = msg

            if duration_sec > 0:
                task = asyncio.create_task(self.progress_loop(chat_id, msg, duration_sec))
                self.progress_tasks[chat_id] = task

        except Exception as e:
            LOGGER.error(f"Error in on_song_start: {e}", exc_info=True)

    async def on_seek(self, chat_id, song, seconds):
        LOGGER.info(f"Seek in {chat_id}: {seconds}s")

        msg = self.now_playing_msg.get(chat_id)
        if not msg:
            return

        direction = "Fᴏʀᴡᴀʀᴅᴇᴅ" if seconds > 0 else "Rᴇᴡɪɴᴅᴇᴅ"

        caption, entities = build_caption(
            song.title,
            song.url,
            song.duration_text,
            song.requested_by,
            header=f"{direction} {abs(seconds)}s\n\nNᴏᴡ Pʟᴀʏɪɴɢ"
        )

        try:
            await msg.delete()
        except Exception:
            pass

        old_task = self.progress_tasks.get(chat_id)
        if old_task:
            old_task.cancel()

        from Pronova.Bot import engine
        current_time = engine.vc.player.current_time(chat_id)
        duration_sec = time_to_sec(song.duration_text)

        if duration_sec > 0:
            bar = get_progress_bar(current_time, duration_sec)
            time_str = f"{format_time(current_time)} {bar} {format_time(duration_sec)}"
        else:
            time_str = "00:00 ▬▬▬▬▬▬▬▬▬▬ 00:00"

        try:
            thumb = await generate(song)

            new_msg = await self.app.send_photo(
                chat_id,
                photo=thumb,
                caption=caption,
                caption_entities=entities,
                reply_markup=control_buttons(time_str)
            )

            self.now_playing_msg[chat_id] = new_msg

            if duration_sec > 0:
                task = asyncio.create_task(self.progress_loop(chat_id, new_msg, duration_sec))
                self.progress_tasks[chat_id] = task

        except Exception as e:
            LOGGER.error(f"Error in on_seek: {e}", exc_info=True)

    async def on_queue_add(self, chat_id, song, position):
        LOGGER.info(f"Song added to queue {chat_id}: {song.title} at {position}")

        if position == 1:
            return

        caption, entities = build_caption(
            song.title,
            song.url,
            song.duration_text,
            song.requested_by,
            header="Aᴅᴅᴇᴅ Tᴏ Qᴜᴇᴜᴇ",
            position=position
        )

        try:
            thumb = await generate(song)

            msg = await self.app.send_photo(
                chat_id,
                photo=thumb,
                caption=caption,
                caption_entities=entities
            )

            asyncio.create_task(self._auto_delete(msg, QUEUE_DELETE_AFTER))

        except Exception as e:
            LOGGER.error(f"Error in on_queue_add: {e}", exc_info=True)

    async def on_song_end(self, chat_id, song):
        LOGGER.info(f"Song ended in {chat_id}: {song.title}")

        task = self.progress_tasks.pop(chat_id, None)
        if task:
            task.cancel()

        msg = self.now_playing_msg.pop(chat_id, None)

        if msg:
            try:
                await msg.delete()
            except Exception:
                pass

    async def on_vc_closed(self, chat_id):
        LOGGER.info(f"Voice chat closed in {chat_id}")

        task = self.progress_tasks.pop(chat_id, None)
        if task:
            task.cancel()

        msg = self.now_playing_msg.pop(chat_id, None)

        if msg:
            try:
                await msg.delete()
            except Exception:
                pass

        try:
            msg = await self.app.send_message(
                chat_id,
                "🔴 Vᴏɪᴄᴇ Cʜᴀᴛ Eɴᴅᴇᴅ\n\n🧹 Qᴜᴇᴜᴇ Cʟᴇᴀʀᴇᴅ & Pʟᴀʏᴇʀ Sᴛᴏᴘᴘᴇᴅ."
            )

            asyncio.create_task(self._auto_delete(msg, VC_END_DELETE_AFTER))

        except Exception as e:
            LOGGER.error(f"Error in on_vc_closed: {e}", exc_info=True)

    async def _auto_delete(self, msg, delay):
        try:
            await asyncio.sleep(delay)
            await msg.delete()
        except Exception:
            pass
    
