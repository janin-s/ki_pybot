from discord.ext import commands

class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    async def msg(self, ctx):
        """"Safe texts using a shorthand"""

        # why dont i have database :(