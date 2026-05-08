class Settings:
    def __init__(self):
        self.cookies: str | None = None
        self.require_cookies: bool = True
        self.debug: bool = False
        self.auto_delete_queue: bool = True
        self.auto_delete_nowplaying: bool = True
        self.default_volume: int = 200
        self.experimental: bool = False

    def __repr__(self):
        return (
            f"<Settings debug={self.debug} "
            f"cookies={'Yes' if self.cookies else 'No'} "
            f"require_cookies={self.require_cookies}>"
        )


settings = Settings()
