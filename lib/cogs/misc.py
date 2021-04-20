from discord.ext.commands import Cog
from discord.ext.commands import command


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")
            print("misc cog ready")

    @command()
    async def amongus(self, ctx):
        """switches channel limit for Pannekecke from infinity to 99 and back"""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
        else:
            channel = await self.bot.fetch_channel(706617584631677031)
        current_limit = channel.user_limit
        if current_limit == 0:
            await channel.edit(user_limit=99)
            await ctx.send("among us modus (user anzahl sichtbar) aktiviert")
        else:
            await channel.edit(user_limit=99)
            await ctx.send("among us modus (user anzahl sichtbar) deaktiviert")


def setup(bot):
    bot.add_cog(Misc(bot))
