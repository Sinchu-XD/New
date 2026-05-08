import asyncio
from traceback import format_exc

from pytgcalls import PyTgCalls, filters
from pytgcalls.types import (
    MediaStream,
    AudioQuality,
    VideoQuality,
    StreamEnded,
    ChatUpdate,
)

from Pronova.Utils.Logger import LOGGER


class _NativeEngine:
    def __init__(self, app):
        self._core = PyTgCalls(app)
        self.on_end = None
        self.on_vc_closed = None

        self._ending: set = set()
        self._stopped: set = set()

        LOGGER.info("NativeEngine initialized")

        @self._core.on_update(filters.stream_end())
        async def _ended(_, update: StreamEnded):
            chat_id = update.chat_id

            if chat_id in self._ending:
                return

            self._ending.add(chat_id)
            LOGGER.info(f"[STREAM END] {chat_id}")

            try:
                if self.on_end:
                    await self.on_end(chat_id)
            except Exception:
                LOGGER.error(f"[STREAM END ERROR]\n{format_exc()}")
            finally:
                self._ending.discard(chat_id)

        @self._core.on_update(
            filters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT)
        )
        async def _vc_closed(_, update: ChatUpdate):
            chat_id = update.chat_id
            LOGGER.warning(f"[VC CLOSED] {chat_id}")

            if chat_id in self._stopped:
                return

            try:
                if self.on_vc_closed:
                    await self.on_vc_closed(chat_id)
            except Exception:
                LOGGER.error(f"[VC CLOSED ERROR]\n{format_exc()}")

    async def start(self):
        LOGGER.info("Starting PyTgCalls engine")
        await self._core.start()
        LOGGER.info("PyTgCalls engine started")

    async def play(self, chat_id: int, stream: str, start_time: int = 0, video: bool = False):
        if not stream:
            raise ValueError("Stream URL is empty")

        ffmpeg_params = f"-ss {start_time}" if start_time > 0 else None

        try:
            if video:
                media = MediaStream(
                    media_path=stream,
                    audio_parameters=AudioQuality.STUDIO,
                    video_parameters=VideoQuality.FHD_1080p,
                    ffmpeg_parameters=ffmpeg_params,
                )
            else:
                media = MediaStream(
                    media_path=stream,
                    audio_parameters=AudioQuality.STUDIO,
                    video_flags=MediaStream.Flags.IGNORE,
                    ffmpeg_parameters=ffmpeg_params,
                )

            await self._core.play(chat_id, media)
            self._stopped.discard(chat_id)
            LOGGER.info(f"[STREAM STARTED] {chat_id}")

        except Exception:
            LOGGER.error(f"[PLAY ERROR] {chat_id}\n{format_exc()}")
            raise

    async def stop(self, chat_id: int):
        if chat_id in self._stopped:
            return

        self._stopped.add(chat_id)
        LOGGER.warning(f"[STOP] {chat_id}")

        try:
            await self._core.leave_call(chat_id)
        except Exception:
            pass
        finally:
            self._stopped.discard(chat_id)

    async def pause(self, chat_id: int):
        await self._core.pause(chat_id)

    async def resume(self, chat_id: int):
        await self._core.resume(chat_id)

    async def mute(self, chat_id: int):
        await self._core.mute(chat_id)

    async def unmute(self, chat_id: int):
        await self._core.unmute(chat_id)

    async def change_volume(self, chat_id: int, volume: int = 200):
        volume = max(0, min(volume, 200))
        await self._core.change_volume_call(chat_id, volume)
