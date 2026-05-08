import logging
import sys
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "pronova.log")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s — %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_handler_stream = logging.StreamHandler(sys.stdout)
_handler_stream.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

_handler_file = RotatingFileHandler(
    LOG_FILE,
    maxBytes=50_000_000,
    backupCount=10,
    encoding="utf-8",
)
_handler_file.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

logging.basicConfig(level=logging.WARNING, handlers=[_handler_stream, _handler_file])

for noisy in ("pyrogram", "pytgcalls", "ntgcalls", "asyncio"):
    logging.getLogger(noisy).setLevel(logging.ERROR)

LOGGER = logging.getLogger("Pronova")
LOGGER.setLevel(logging.INFO)


def set_debug(enabled: bool):
    level = logging.DEBUG if enabled else logging.INFO
    LOGGER.setLevel(level)
    LOGGER.info(f"Log level set to {'DEBUG' if enabled else 'INFO'}")
