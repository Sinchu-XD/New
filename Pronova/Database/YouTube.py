import aiohttp
import time
import urllib.parse

from .Core import db


_session = None


async def get_session():
    global _session
    if _session is None or _session.closed:
        timeout = aiohttp.ClientTimeout(total=12)
        _session = aiohttp.ClientSession(timeout=timeout)
    return _session


def get_expire_time(url):
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        expire = qs.get("expire")
        if not expire:
            return None
        return int(expire[0])
    except:
        return None


async def is_stream_valid(url, logger=None):
    try:
        session = await get_session()

        now = int(time.time())
        expire_time = get_expire_time(url)

        if logger:
            logger.info(f"[STREAM URL] {url}")

        if expire_time:
            remaining = expire_time - now
            if logger:
                logger.info(f"[STREAM EXPIRE] {expire_time} | Remaining: {remaining}s")

            if remaining <= 120:
                if logger:
                    logger.warning("[STREAM STATUS] EXPIRED / EXPIRING SOON")
                return False

        headers = {
            "Range": "bytes=0-512",
            "User-Agent": "Mozilla/5.0"
        }

        async with session.get(url, headers=headers, allow_redirects=True) as resp:
            if resp.status not in (200, 206):
                if logger:
                    logger.warning(f"[STREAM STATUS] INVALID STATUS {resp.status}")
                return False

            content_type = resp.headers.get("Content-Type", "")
            if "audio" not in content_type and "video" not in content_type:
                if logger:
                    logger.warning(f"[STREAM STATUS] INVALID TYPE {content_type}")
                return False

            chunk = await resp.content.read(512)
            if not chunk:
                if logger:
                    logger.warning("[STREAM STATUS] EMPTY DATA")
                return False

            if logger:
                logger.info("[STREAM STATUS] VALID")

            return True

    except Exception as e:
        if logger:
            logger.error(f"[STREAM ERROR] {e}")
        return False


async def get_stream_cache(key, logger=None):
    try:
        data = await db.yt_stream_cache.find_one({"_id": key})
        if not data:
            return None

        stream = data.get("stream")
        if not stream:
            return None

        expire_time = get_expire_time(stream)

        if expire_time:
            remaining = expire_time - int(time.time())
            if remaining <= 120:
                await db.yt_stream_cache.delete_one({"_id": key})
                return None

        is_valid = await is_stream_valid(stream, logger)

        if not is_valid:
            await db.yt_stream_cache.delete_one({"_id": key})
            return None

        return stream

    except Exception:
        return None


async def set_stream_cache(key, stream):
    try:
        if not stream:
            return

        await db.yt_stream_cache.update_one(
            {"_id": key},
            {
                "$set": {
                    "stream": stream,
                    "created_at": time.time()
                }
            },
            upsert=True
        )
    except Exception:
        pass


async def get_search_cache(key):
    try:
        data = await db.yt_search_cache.find_one({"_id": key})
        if not data:
            return None
        return data.get("data")
    except Exception:
        return None


async def set_search_cache(key, data):
    try:
        await db.yt_search_cache.update_one(
            {"_id": key},
            {
                "$set": {
                    "data": data,
                    "created_at": time.time()
                }
            },
            upsert=True
        )
    except Exception:
        pass


async def close_session():
    global _session
    if _session and not _session.closed:
        await _session.close()
