import discord
from discord.ext.commands import Cog, command

from lib.bot import Bot


class Status(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("status")

    @command(name="status")
    async def status(self, ctx, *, status):
        """Setze einen neuen Status mit !status {status}"""
        await ctx.send(f" Changed current status to: {status}")
        await self.bot.change_presence(activity=discord.Game(f'{status}'), status=discord.Status.online)


def setup(bot):
    bot.add_cog(Status(bot))
