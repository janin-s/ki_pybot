from discord.ext.commands import *


class PMsg(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("personalized_msg")

    @command(name="guna")
    async def guna(self, ctx):
        print("guna called")
        """KI wünscht allen eine gute Nacht"""
        user_name = ctx.message.author.display_name
        await ctx.send(user_name + ' wünscht allen eine GuNa!')


def setup(bot):
    bot.add_cog(PMsg(bot))
