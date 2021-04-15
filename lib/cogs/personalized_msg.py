from discord.ext.commands import Cog
from discord.ext.commands import command


class PMsg(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("personalized_msg")
            print("personalized_msg cog ready")

    @command(name="msg")
    async def guna(self, ctx):
        pass


def setup(bot):
    bot.add_cog(PMsg(bot))
