import re

import discord
from discord.ext.commands import Cog, command, Context
from leakcheck import LeakCheckAPI

from lib.bot import Bot


class Osint(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.leakcheck = LeakCheckAPI()
        self.leakcheck.set_key(self.bot.config.leakcheck_api_key)

    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("OSINT enabled!")

    @command()
    async def osint(self, ctx: Context, email=None):
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not email or not re.fullmatch(email_regex, email):
            await ctx.send("`!osint max@gmail.com`")
            return
        results = self.leakcheck.lookup(email)
        if not results:
            await ctx.send("Konnte keine Daten finden. :(")
            return
        with open("/tmp/osint.txt", "w") as f:
            for result in results:
                line = f"source: {', '.join(result['sources'])}\n" \
                       f"info: {result['line']}\n" \
                       f"last_breach: {result['last_breach']}\n"
                f.write(line + "\n")
                f.write("\n")
        await ctx.send(f"Infos zu `{email}`:", file=discord.File("/tmp/osint.txt"))


def setup(bot):
    bot.add_cog(Osint(bot))
