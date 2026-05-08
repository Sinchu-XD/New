from Pronova.Utils.Logger import LOGGER  # ✅ ADDED

import os
import re
import asyncio
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from .Models import Song as Track

import hashlib


# Modern frosted glass design constants
PANEL_W, PANEL_H = 763, 545
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 88
TRANSPARENCY = 170

THUMB_W, THUMB_H = 542, 273
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + 36

TITLE_X = 377
TITLE_Y = THUMB_Y + THUMB_H + 10
META_Y = TITLE_Y + 45

BAR_X, BAR_Y = 388, META_Y + 45
BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580

DEFAULT_THUMB = "https://picsum.photos/1280/720"


def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    ellipsis = "…"
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis


class Thumbnail:
    def __init__(self):
        try:
            self.title_font = ImageFont.truetype("Raleway-Bold.ttf", 32)
            self.regular_font = ImageFont.truetype("Inter-Light.ttf", 18)
        except OSError:
            self.title_font = self.regular_font = ImageFont.load_default()

    async def save_thumb(self, output_path: str, url: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not url:
            url = DEFAULT_THUMB

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise Exception(f"Invalid Thumb Status: {resp.status}")

                    data = await resp.read()

                    # ✅ ADDED CHECK
                    if not data or len(data) < 5000:
                        raise Exception("Empty or small image data")

                    with open(output_path, "wb") as f:
                        f.write(data)

        except Exception as e:
            LOGGER.warning(f"Thumbnail download failed: {e} | Using default")

            async with aiohttp.ClientSession() as session:
                async with session.get(DEFAULT_THUMB) as resp:
                    data = await resp.read()

                    # ✅ SAFE WRITE
                    if data:
                        with open(output_path, "wb") as f:
                            f.write(data)

        return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            song_id = hashlib.md5((song.url or song.title).encode()).hexdigest()

            temp = f"cache/temp_{song_id}.jpg"
            output = f"cache/{song_id}_modern.png"

            # ✅ CACHE VALIDATION ADDED
            if os.path.exists(output):
                try:
                    if os.path.getsize(output) > 10000:
                        return output
                    else:
                        LOGGER.warning("Corrupt cache detected, regenerating")
                        os.remove(output)
                except Exception as e:
                    LOGGER.warning(f"Cache check error: {e}")

            await self.save_thumb(temp, song.thumb)

            # ✅ TEMP VALIDATION
            if not os.path.exists(temp) or os.path.getsize(temp) < 5000:
                raise Exception("Downloaded thumbnail invalid")

            return await asyncio.get_event_loop().run_in_executor(
                None, self._generate_sync, temp, output, song, size
            )

        except Exception as e:
            LOGGER.error(f"Thumbnail generate failed: {e}", exc_info=True)
            return DEFAULT_THUMB

    def _generate_sync(self, temp: str, output: str, song: Track, size=(1280, 720)) -> str:
        try:
            with Image.open(temp) as temp_img:
                base = temp_img.resize(size).convert("RGBA")

            bg = ImageEnhance.Brightness(
                base.filter(ImageFilter.BoxBlur(10))
            ).enhance(0.6)

            panel_area = bg.crop(
                (PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H)
            )
            overlay = Image.new("RGBA", (PANEL_W, PANEL_H),
                                (255, 255, 255, TRANSPARENCY))
            frosted = Image.alpha_composite(panel_area, overlay)

            mask = Image.new("L", (PANEL_W, PANEL_H), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H), 50, fill=255)
            bg.paste(frosted, (PANEL_X, PANEL_Y), mask)

            thumb = base.resize((THUMB_W, THUMB_H))
            tmask = Image.new("L", thumb.size, 0)
            ImageDraw.Draw(tmask).rounded_rectangle(
                (0, 0, THUMB_W, THUMB_H), 20, fill=255)
            bg.paste(thumb, (THUMB_X, THUMB_Y), tmask)

            draw = ImageDraw.Draw(bg)

            clean_title = re.sub(r"\W+", " ", song.title).title()
            draw.text(
                (TITLE_X, TITLE_Y),
                trim_to_width(clean_title, self.title_font, MAX_TITLE_WIDTH),
                fill="black",
                font=self.title_font
            )

            draw.text(
                (TITLE_X, META_Y),
                f"{song.channel} | {song.views or 'Unknown Views'}",
                fill="black",
                font=self.regular_font
            )

            draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)],
                      fill="red", width=6)
            draw.line([(BAR_X + BAR_RED_LEN, BAR_Y),
                      (BAR_X + BAR_TOTAL_LEN, BAR_Y)], fill="gray", width=5)
            draw.ellipse([(BAR_X + BAR_RED_LEN - 7, BAR_Y - 7),
                         (BAR_X + BAR_RED_LEN + 7, BAR_Y + 7)], fill="red")

            draw.text((BAR_X, BAR_Y + 15), "00:00",
                      fill="black", font=self.regular_font)

            is_live = getattr(song, 'is_live', False)
            end_text = "Live" if is_live else song.duration
            draw.text(
                (BAR_X + BAR_TOTAL_LEN - (90 if is_live else 60), BAR_Y + 15),
                end_text,
                fill="red" if is_live else "black",
                font=self.regular_font
            )

            icons_path = "HasiiMusic/helpers/play_icons.png"
            if os.path.isfile(icons_path):
                with Image.open(icons_path) as icons_img:
                    ic = icons_img.resize((ICONS_W, ICONS_H)).convert("RGBA")
                    r, g, b, a = ic.split()
                    black_ic = Image.merge(
                        "RGBA",
                        (r.point(lambda _: 0),
                         g.point(lambda _: 0),
                         b.point(lambda _: 0),
                         a)
                    )
                    bg.paste(black_ic, (ICONS_X, ICONS_Y), black_ic)

            bg.save(output)

            # ✅ OUTPUT VALIDATION
            if not os.path.exists(output) or os.path.getsize(output) < 10000:
                raise Exception("Generated thumbnail invalid")

            try:
                os.remove(temp)
            except OSError:
                pass

            return output

        except Exception as e:
            LOGGER.error(f"_generate_sync failed: {e}", exc_info=True)
            return DEFAULT_THUMB
