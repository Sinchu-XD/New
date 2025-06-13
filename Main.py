import json
import string
import random
import os
from pyrogram import Client, filters
from pyrogram.types import Message

# ----------------- CONFIGURATION -----------------
API_ID = 6067591  # 🔁 Replace with your API ID
API_HASH = "94e17044c2393f43fda31d3afe77b26b"  # 🔁 Replace with your API HASH
BOT_TOKEN = "7946373751:AAEnaR6L6-8d9cYYlOCS1UqmXSjRXFjARVI"  # 🔁 Replace with your BOT Token

DB_PATH = "files_db.json"

# ----------------- INIT BOT -----------------
bot = Client("FileStoreBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ----------------- DB FUNCTIONS -----------------
def generate_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def load_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

# ----------------- COMMAND HANDLERS -----------------
@bot.on_message(filters.private & filters.command("start"))
async def start_cmd(_, message: Message):
    if len(message.command) > 1:
        file_id = message.command[1]
        db = load_db()
        if file_id in db:
            media_id = db[file_id]

            try:
                # Try sending as document
                await bot.send_document(
                    chat_id=message.chat.id,
                    document=media_id,
                    protect_content=True,
                    caption="🔒 This file is protected. No forwarding, no copying, no downloading."
                )
            except ValueError as e:
                # If it's not a document, try sending as video
                if "VIDEO" in str(e):
                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=media_id,
                        protect_content=True,
                        caption="🔒 This file is protected. No forwarding, no copying, no downloading."
                    )
                elif "AUDIO" in str(e):
                    await bot.send_audio(
                        chat_id=message.chat.id,
                        audio=media_id,
                        protect_content=True,
                        caption="🔒 This file is protected. No forwarding, no copying, no downloading."
                    )
                else:
                    await message.reply("❌ Unsupported media type.")
        else:
            await message.reply("❌ Invalid or expired file link.")
    else:
        await message.reply("👋 Send me any file and I will give you a secure shareable link!")

# ----------------- FILE RECEIVER -----------------
@bot.on_message(filters.private & filters.document | filters.video | filters.audio)
async def save_file(_, message: Message):
    media = message.document or message.video or message.audio
    file_id = media.file_id
    unique_id = generate_id()

    db = load_db()
    db[unique_id] = file_id
    save_db(db)

    bot_username = (await bot.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={unique_id}"
    await message.reply(
        f"✅ File Saved Successfully!\n\n🔗 Share this link:\n`{share_link}`\n\n"
        "Whoever opens this will get the same file, but fully protected (no copy, no forward, no download).",
        quote=True
    )

# ----------------- START BOT -----------------
print("✅ Bot is Running...")
bot.run()
  
