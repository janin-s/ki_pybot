from discord.ext.commands import Cog
from discord.ext.commands import command


class Msg(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("msg")
            print("msg cog ready")

    @command(name="msg", aliases=["message"])
    async def msg(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Msg(bot))
