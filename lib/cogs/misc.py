from discord.ext.commands import *
from discord import Game, Status

from lib.db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")

    @command()
    async def amongus(self, ctx):
        """switches channel limit for Pannekecke from infinity to 99 and back"""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
        else:
            await ctx.send("not connected to a voice channel!")
            return
        current_limit = channel.user_limit
        if current_limit == 0:
            await channel.edit(user_limit=99)
            await ctx.send("among us modus (user anzahl sichtbar) aktiviert")
        else:
            await channel.edit(user_limit=0)
            await ctx.send("among us modus (user anzahl sichtbar) deaktiviert")

    @command()
    async def zitat(self, ctx, length=1):
        """!zitat [x]; zitiert die letze[n x] Nachricht[en] und speichert sie in Relikte"""
        zitat: str = ""
        message_list = []
        async for message in ctx.channel.history(limit=length + 1):
            message_list.append(message)
        message_list.reverse()
        for m in message_list:
            zitat += m.autohr.display_name + ": \"" + m.content + "\"\n"
        quote_channel_id = db.field("SELECT quote_channel FROM server_info WHERE guild_id = ?", ctx.guild)
        if quote_channel_id is None:
            quote_channel_id = ctx.channel.id
        quote_channel = await self.bot.fetch_channel(quote_channel_id)
        await quote_channel.send(zitat)

    @Cog.listener()
    async def on_message(self, message):
        #for debugging
        print(f"got message: {str(message)}")


def setup(bot):
    bot.add_cog(Misc(bot))
