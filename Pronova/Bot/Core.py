from pyrogram import Client
from Config import *
from Pronova.Player.Core import VoiceEngine

bot = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user = Client(
    "music_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

engine = VoiceEngine(user, cookies=COOKIES_PATH)
