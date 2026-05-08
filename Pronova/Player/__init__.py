import sys
import os
import logging
from contextlib import contextmanager
from pytgcalls import idle as _idle

try:
    from .Settings import settings
    DEBUG = getattr(settings, "debug", False)
except Exception:
    DEBUG = False


logging.getLogger("pytgcalls").setLevel(logging.CRITICAL)
logging.getLogger("ntgcalls").setLevel(logging.CRITICAL)


@contextmanager
def _suppress_stdout():
    if DEBUG:
        yield
        return

    try:
        with open(os.devnull, "w") as devnull:
            old_out = sys.stdout
            old_err = sys.stderr
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                yield
            finally:
                sys.stdout = old_out
                sys.stderr = old_err
    except Exception:
        yield


async def idle():
    try:
        with _suppress_stdout():
            await _idle()
    except Exception:
        pass
