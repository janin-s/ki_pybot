import re

import discord
from discord.ext.commands import Cog, command, Context
from claude_api import Client

from lib.bot import Bot


class Claude(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.client_api = Client(self.bot.config.claude_session_cookie)

    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Claude enabled!")

    def get_response(self, prompt, attachments):
        new_chat = self.client_api.create_new_chat()
        new_chat_id = new_chat["uuid"]
        attachment = None
        if attachments:
            a = attachments[0]
            if a.content_type not in ["application/pdf", "application/txt"]:
                return "Please only upload PDF or TXT files."
            attachment = f"/tmp/{a.filename}"
            await a.save(attachment)
        response = self.client_api.send_message(prompt, new_chat_id, attachment)
        return response

    @command()
    async def claude(self, ctx: Context, prompt=None):
        if not prompt:
            await ctx.send("!claude <prompt>")
            return
        response = self.get_response(prompt, ctx.message.attachments)
        return await ctx.send(response)


def setup(bot):
    bot.add_cog(Claude(bot))
