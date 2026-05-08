from .Native import _NativeEngine
from .Controller import VoiceController


class VoiceEngine:
    def __init__(self, app, cookies: str | None = None):
        self._engine = _NativeEngine(app)
        self.vc = VoiceController(self._engine, cookies=cookies)

    async def start(self):
        await self._engine.start()
