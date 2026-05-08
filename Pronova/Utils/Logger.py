import logging
import sys
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.environ.get("LOG_DIR", "/tmp/logs")
LOG_FILE = os.path.join(LOG_DIR, "pronova.log")

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s — %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_handler_stream = logging.StreamHandler(sys.stdout)
_handler_stream.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

_handlers: list[logging.Handler] = [_handler_stream]

try:
    _handler_file = RotatingFileHandler(
        LOG_FILE,
        maxBytes=50_000_000,
        backupCount=10,
        encoding="utf-8",
    )
    _handler_file.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    _handlers.append(_handler_file)
except OSError as e:
    print(f"[LOGGER] File logging unavailable: {e}", file=sys.stderr)

logging.basicConfig(level=logging.WARNING, handlers=_handlers)

for _noisy in ("pyrogram", "pytgcalls", "ntgcalls", "asyncio"):
    logging.getLogger(_noisy).setLevel(logging.ERROR)

LOGGER = logging.getLogger("Pronova")
LOGGER.setLevel(logging.INFO)


def set_debug(enabled: bool) -> None:
    level = logging.DEBUG if enabled else logging.INFO
    LOGGER.setLevel(level)
    LOGGER.info(f"Log level set to {'DEBUG' if enabled else 'INFO'}")
