import time
from traceback import format_exc

from Pronova.Utils.Queue import SongQueue
from Pronova.Utils.Logger import LOGGER


class Player:
    def __init__(self, engine):
        self.engine = engine
        self.queues: dict[int, SongQueue] = {}
        self.start_time: dict[int, float] = {}
        LOGGER.info("Player initialized")

    def _queue(self, chat_id: int) -> SongQueue:
        return self.queues.setdefault(chat_id, SongQueue())

    def current_time(self, chat_id: int) -> int:
        try:
            start = self.start_time.get(chat_id)
            if not start:
                return 0
            elapsed = max(int(time.monotonic() - start), 0)
            q = self.queues.get(chat_id)
            if q and q.current():
                q.current().position = elapsed
            return elapsed
        except Exception:
            LOGGER.error(f"[TIME ERROR]\n{format_exc()}")
            return 0

    async def play(self, chat_id: int, song, video: bool = False) -> int:
        LOGGER.info(f"[PLAY REQUEST] {repr(song.title)} in {chat_id}")
        try:
            q = self._queue(chat_id)
            pos = q.add(song)
            LOGGER.info(f"[QUEUE ADD] {repr(song.title)} at position {pos}")
            if pos == 1:
                try:
                    await self.engine.play(chat_id, song.stream, video=song.is_video)
                    self.start_time[chat_id] = time.monotonic()
                    song.position = 0
                    LOGGER.info(f"[STREAM STARTED] {repr(song.title)}")
                except Exception:
                    LOGGER.error(f"[PLAY ENGINE ERROR] {repr(song.title)}\n{format_exc()}")
                    q.pop_last()
                    self.start_time.pop(chat_id, None)
                    raise
            return pos
        except Exception:
            LOGGER.error(f"[PLAY ERROR]\n{format_exc()}")
            raise

    async def seek(self, chat_id: int, seconds: int) -> bool:
        LOGGER.info(f"[SEEK] {chat_id} | {seconds}s")
        try:
            q = self.queues.get(chat_id)
            if not q or not q.current():
                LOGGER.warning("[SEEK FAILED] No current song")
                return False
            song = q.current()
            new_time = max(self.current_time(chat_id) + seconds, 0)
            duration = getattr(song, "duration_sec", 0)
            if duration > 0 and new_time >= duration:
                LOGGER.warning("[SEEK FAILED] Exceeds duration")
                return False
            await self.engine.play(chat_id, song.stream, start_time=new_time, video=song.is_video)
            self.start_time[chat_id] = time.monotonic() - new_time
            song.position = new_time
            return True
        except Exception:
            LOGGER.error(f"[SEEK ERROR]\n{format_exc()}")
            return False

    async def skip(self, chat_id: int):
        LOGGER.info(f"[SKIP] {chat_id}")
        try:
            q = self.queues.get(chat_id)
            if not q:
                LOGGER.warning("[SKIP FAILED] No queue")
                return None

            current = q.current()
            if current:
                if getattr(current, "loop_left", 0) > 0:
                    current.loop_left -= 1
                    LOGGER.info("[LOOP CONTINUE]")
                    return await self._restart_current(chat_id)
                if getattr(q, "infinite_loop", False):
                    LOGGER.info("[INFINITE LOOP]")
                    return await self._restart_current(chat_id)

            nxt = q.next()
            LOGGER.info(f"[NEXT SONG] {repr(nxt.title) if nxt else 'queue empty'}")

            if not nxt:
                LOGGER.warning("[QUEUE EMPTY] Stopping VC")
                self.start_time.pop(chat_id, None)
                try:
                    await self.engine.stop(chat_id)
                except Exception:
                    LOGGER.error(f"[STOP ERROR]\n{format_exc()}")
                return None

            stream = nxt.stream
            if not stream or not stream.startswith("http"):
                cached = q.get_prefetched_stream(nxt.url or "")
                if cached:
                    nxt.stream = cached
                    stream = cached
                    LOGGER.info(f"[PREFETCH HIT] {repr(nxt.title)}")

            await self.engine.play(chat_id, stream, video=nxt.is_video)
            self.start_time[chat_id] = time.monotonic()
            nxt.position = 0
            LOGGER.info(f"[PLAYING NEXT] {repr(nxt.title)}")
            return nxt

        except Exception:
            LOGGER.error(f"[SKIP ERROR]\n{format_exc()}")
            return None

    async def _restart_current(self, chat_id: int):
        try:
            q = self.queues.get(chat_id)
            if not q or not q.current():
                return None
            song = q.current()
            await self.engine.play(chat_id, song.stream, video=song.is_video)
            self.start_time[chat_id] = time.monotonic()
            song.position = 0
            LOGGER.info(f"[RESTART SONG] {repr(song.title)}")
            return song
        except Exception:
            LOGGER.error(f"[RESTART ERROR]\n{format_exc()}")
            return None

    async def previous(self, chat_id: int):
        LOGGER.info(f"[PREVIOUS] {chat_id}")
        try:
            q = self.queues.get(chat_id)
            if not q:
                return None
            prev = q.previous()
            if not prev:
                LOGGER.warning("[NO PREVIOUS SONG]")
                return None
            await self.engine.play(chat_id, prev.stream, video=prev.is_video)
            self.start_time[chat_id] = time.monotonic()
            prev.position = 0
            LOGGER.info(f"[PLAYING PREVIOUS] {repr(prev.title)}")
            return prev
        except Exception:
            LOGGER.error(f"[PREVIOUS ERROR]\n{format_exc()}")
            return None

    async def stop(self, chat_id: int):
        LOGGER.warning(f"[STOP] {chat_id}")
        try:
            q = self.queues.get(chat_id)
            if q:
                q.clear()
            self.start_time.pop(chat_id, None)
            await self.engine.stop(chat_id)
        except Exception:
            LOGGER.error(f"[STOP ERROR]\n{format_exc()}")

    async def pause(self, chat_id: int):
        LOGGER.info(f"[PAUSE] {chat_id}")
        await self.engine.pause(chat_id)

    async def resume(self, chat_id: int):
        LOGGER.info(f"[RESUME] {chat_id}")
        await self.engine.resume(chat_id)

    async def mute(self, chat_id: int):
        LOGGER.info(f"[MUTE] {chat_id}")
        await self.engine.mute(chat_id)

    async def unmute(self, chat_id: int):
        LOGGER.info(f"[UNMUTE] {chat_id}")
        await self.engine.unmute(chat_id)

    async def volume(self, chat_id: int, volume: int):
        volume = max(0, min(volume, 200))
        LOGGER.info(f"[VOLUME] {chat_id} -> {volume}")
        await self.engine.change_volume(chat_id, volume)

    def set_loop(self, chat_id: int, count: int | None = None):
        q = self._queue(chat_id)
        if count is None:
            q.infinite_loop = not q.infinite_loop
            LOGGER.info(f"[TOGGLE LOOP] {q.infinite_loop}")
            return q.infinite_loop
        if count <= 0:
            return 0
        cur = q.current()
        if cur:
            cur.loop_left = max(count - 1, 0)
            LOGGER.info(f"[SET LOOP COUNT] {count}")
            return count
        return 0

    def eta(self, chat_id: int) -> int | None:
        try:
            q = self.queues.get(chat_id)
            if not q or not q.current():
                return None
            elapsed = self.current_time(chat_id)
            dur = getattr(q.current(), "duration_sec", 0)
            return max(dur - elapsed, 0) if dur > 0 else None
        except Exception:
            LOGGER.error(f"[ETA ERROR]\n{format_exc()}")
            return None
