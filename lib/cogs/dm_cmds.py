from discord.ext.commands import Cog
from discord.ext.commands import command


class DMCmds(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("dm_cmds")
            print("dm_cmds cog ready")

    @command(name="hug")
    async def hug(self, ctx):
        pass

    @command(name="punish")
    async def punish(self,ctx):
        pass

def setup(bot):
    bot.add_cog(DMCmds(bot))
