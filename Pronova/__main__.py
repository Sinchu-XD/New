import asyncio

from Pronova.Bot.Core import bot, user, engine
from Pronova.Player import idle
from Pronova.UI.Plugins import Plugin
import Pronova.Plugins

async def main():
    await bot.start()
    await user.start()
    await engine.start()
    engine.vc.load_plugin(Plugin(bot))
    await idle()

if __name__ == "__main__":
    loop = bot.loop
    loop.run_until_complete(main())
