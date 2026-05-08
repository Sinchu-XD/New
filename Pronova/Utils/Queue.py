import asyncio
import random
from collections import deque


class SongQueue:
    def __init__(self):
        self.items: list = []
        self.history: deque = deque(maxlen=20)
        self.infinite_loop: bool = False
        self._prefetch_task: asyncio.Task | None = None
        self._prefetch_cache: dict = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    def add(self, song) -> int | None:
        try:
            self.items.append(song)
            return len(self.items)
        except Exception:
            return None

    def pop_last(self):
        try:
            return self.items.pop() if self.items else None
        except Exception:
            return None

    def current(self):
        try:
            return self.items[0] if self.items else None
        except Exception:
            return None

    def peek_next(self):
        try:
            return self.items[1] if len(self.items) > 1 else None
        except Exception:
            return None

    def next(self):
        try:
            if not self.items:
                return None

            current = self.items[0]
            self.history.appendleft(current)

            if getattr(current, "loop_left", 0) > 0:
                current.loop_left -= 1
                return current

            if self.infinite_loop:
                return current

            self.items.pop(0)
            return self.current()

        except Exception:
            return None

    def previous(self):
        try:
            if not self.history:
                return None
            prev = self.history.popleft()
            self.items.insert(0, prev)
            return prev
        except Exception:
            return None

    def shuffle(self) -> bool:
        try:
            if len(self.items) <= 1:
                return False
            current = self.items.pop(0)
            random.shuffle(self.items)
            self.items.insert(0, current)
            return True
        except Exception:
            return False

    def set_prefetched_stream(self, url: str, stream: str):
        self._prefetch_cache[url] = stream

    def get_prefetched_stream(self, url: str) -> str | None:
        return self._prefetch_cache.pop(url, None)

    def cancel_prefetch(self):
        if self._prefetch_task and not self._prefetch_task.done():
            self._prefetch_task.cancel()
            self._prefetch_task = None

    def clear(self):
        try:
            self.cancel_prefetch()
            self.items.clear()
            self.history.clear()
            self._prefetch_cache.clear()
            self.infinite_loop = False
        except Exception:
            pass
