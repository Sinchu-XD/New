class Song:
    __slots__ = (
        "title", "url", "duration", "views", "stream",
        "requested_by", "loop_left", "thumb", "is_video",
        "channel", "position"
    )

    def __init__(
        self,
        title,
        url,
        duration,
        views,
        stream,
        requested_by,
        channel=None,
        loop_left=0,
        thumb=None,
        is_video=False
    ):
        self.title = title or "Unknown"
        self.url = url
        self.duration = duration
        self.views = views
        self.stream = stream
        self.requested_by = requested_by or "Unknown"
        self.loop_left = loop_left or 0
        self.thumb = thumb
        self.is_video = is_video
        self.channel = channel
        self.position = 0

    @property
    def duration_sec(self) -> int:
        return self._to_seconds(self.duration)

    @property
    def duration_text(self) -> str:
        sec = self.duration_sec
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def _to_seconds(self, d) -> int:
        try:
            if d is None:
                return 0
            if isinstance(d, int):
                return d
            if isinstance(d, str):
                if ":" in d:
                    parts = [int(p) for p in d.split(":")]
                    if len(parts) == 3:
                        h, m, s = parts
                        return h * 3600 + m * 60 + s
                    if len(parts) == 2:
                        m, s = parts
                        return m * 60 + s
                return int(d)
            return int(d)
        except Exception:
            return 0

    def __repr__(self):
        return f"<Song title={self.title!r} duration={self.duration_text}>"
