import discord
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext import commands


class DMCmds(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("dm_cmds")
            print("dm_cmds cog ready")

    @command(name="hug")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hug(self, ctx):
        """umarmt alle mentioned user privat. 1 min cooldown"""
        users = ctx.message.mentions
        for user in users:
            current_id = user.id
            if current_id == 709865255479672863:
                user = ctx.message.author
                sender = "KI"
                await ctx.send("KI hat dich auch lieb! :)")
            else:
                sender = ctx.message.author.display_name
            await ctx.send(f"{sender} versendet eine Umarmung an {user.display_name}!")

            dm_channel = user.dm_channel
            try:
                if dm_channel is None:
                    dm_channel = await user.create_dm()
                await dm_channel.send(f"Liebe! {sender} sendet dir eine Umarmung!")
                await dm_channel.send("https://i.pinimg.com/originals/e2/f7/2a/e2f72a771865ea0d74895cb2c2199a83.gif")
            except discord.Forbidden:
                pass
        await ctx.message.delete()

    @command(name="punish")
    async def punish(self, ctx):
        pass


def setup(bot):
    bot.add_cog(DMCmds(bot))
