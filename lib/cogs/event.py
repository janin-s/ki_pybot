import discord
from discord.ext.commands import Cog
from discord.ext.commands import command


class Event(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("event")
            print("event cog ready")

    @command(name="event")
    async def event(self, ctx, *, event):
        """Setze ein neues Event mit !event {event}"""
        await ctx.send(f" Changed current event to: {event}")
        await self.bot.change_presence(activity=discord.Game(f'{event}'), status=discord.Status.online)


def setup(bot):
    bot.add_cog(Event(bot))
