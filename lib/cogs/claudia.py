import re

import discord
from discord.ext.commands import Cog, command, Context
from lib.utils import llm
from pathlib import Path

from lib.bot import Bot


class Claudia(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.role_desc = (
            Path("res/claudia_prompt.txt").read_text().replace("\n", " ").strip()
        )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Gottköniginclaudia ist auferstanden!")

    async def send_message_as_claudia(self, message: str, channel, guild, file):
        guild_webhooks: list[discord.Webhook] = await guild.webhooks()
        webhooks_filtered: list[discord.Webhook] = [
            w for w in guild_webhooks if str(channel.id) in w.name
        ]
        if not webhooks_filtered:
            webhook: discord.Webhook = await channel.create_webhook(
                name=f"say-cmd-hook-{channel.id}"
            )
        else:
            webhook: discord.Webhook = webhooks_filtered[0]
        if file:
            await webhook.send(
            content=message,
            username="Prof. Claudi",
            avatar_url="https://profile-images.xing.com/images/ca8686b5c8f66c1f03e9cd327e765ab1-1/claudia-eckert.1024x1024.jpg",
            file=file,
        )
        else: 
            await webhook.send(
            content=message,
            username="Prof. Claudi",
            avatar_url="https://profile-images.xing.com/images/ca8686b5c8f66c1f03e9cd327e765ab1-1/claudia-eckert.1024x1024.jpg",
        )

    @Cog.listener()
    async def on_message(self, message):
        if not str(message.content).lower().startswith(
            ("@Claudi ")
        ):
            return

        guild = message.guild
        channel = message.channel
        file_paths = []
        for a in message.attachments:
            if a.content_type not in ["application/pdf", "text/plain"]:
                return await self.send_message_as_claudia(
                    "Als Professorin für Informatik an der TUM erwarte ich PDFs oder reinen Text. Ich bitte Sie höflichst, dass Sie sich an diese Vorgaben halten.",
                    channel,
                    guild,
                    None,
                )
            file_path = f"/tmp/{a.filename}"
            await a.save(file_path)
            file_paths.append(file_path)

        response, costs = llm.claude(self.bot).get_response(
            self.role_desc, message.content.split(" ", 1)[1], file_paths
        )
        if len(response) > 1000:
            with open("/tmp/claudia.txt", "w") as f:
                f.write(response)
            message = f"||Diese Nachricht hat {costs:.2f}ct gekostet||"
            return await self.send_message_as_claudia(
                message, channel, guild, file=discord.File("/tmp/claudia.txt")
            )
        else:
            message = f"{response}\n\n||Diese Nachricht hat {costs:.2f}ct gekostet||"
            return await self.send_message_as_claudia(message, channel, guild, None)


def setup(bot):
    bot.add_cog(Claudia(bot))
