import os
from dotenv import load_dotenv

load_dotenv()


def get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"{name} is missing")
    return value


API_ID = int(get_env("API_ID", required=True))
API_HASH = get_env("API_HASH", required=True)

BOT_TOKEN = get_env("BOT_TOKEN", required=True)

SESSION_STRING = os.getenv("SESSION_STRING")

MONGO_URL = get_env("MONGO_URL", required=True)
DB_NAME = get_env("DB_NAME", "Pronova")

RAPID_API_KEY = get_env("RAPID_API_KEY")

OWNER_ID = int(get_env("OWNER_ID", required=True))

COMMAND_PREFIX = os.getenv("PREFIX", "/")

COOKIES_PATH = os.getenv("COOKIES_PATH")

TEXTS = os.getenv("TEXTS", "")
LINKS = os.getenv("LINKS", "")

LOG_CHAT_ID = int(get_env("LOG_CHAT_ID", required=True))
