from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Game, Status


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")
            print("misc cog ready")

    @command()
    async def event(self, ctx, *, event):
        """Setze ein neues Event mit !event {event}"""
        await ctx.send(f'Current event changed to {event}')
        await self.bot.change_presence(activity=Game(f'{event}'), status=Status.online)

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
        relikte = await self.bot.fetch_channel(705427122151227442)
        await relikte.send(zitat)


def setup(bot):
    bot.add_cog(Misc(bot))
