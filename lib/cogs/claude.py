import re

import discord
from discord.ext.commands import Cog, command, Context
from leakcheck import LeakCheckAPI

from lib.bot import Bot


class Claude(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.leakcheck = LeakCheckAPI()
        self.leakcheck.set_key(self.bot.config.leakcheck_api_key)

    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("OSINT enabled!")

    @command()
    async def claude(self, ctx: Context, prompt=None):
        pass


def setup(bot):
    bot.add_cog(Claude(bot))
