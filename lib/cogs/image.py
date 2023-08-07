import re

import discord
from discord.ext.commands import Cog, command, Context
from sdxl import ImageGenerator

from lib.bot import Bot


class Image(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.client = ImageGenerator()

    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("ImageGenerator enabled!")

    @command()
    async def image(self, ctx: Context, prompt=None):
        if not prompt:
            await ctx.send("!image `prompt`")
            return
        response = self.client.gen_image(prompt=prompt, width=1024, height=1024, count=4)
        for image_url in response["images"]:
            await ctx.send(image_url)


def setup(bot):
    bot.add_cog(Image(bot))
