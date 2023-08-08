import discord
from discord.ext import commands
from discord.ext.commands import Cog, command, Context
from discord.message import Message
from discord.channel import TextChannel
from discord.guild import Guild
import numpy as np
from lib.utils import llm

from pathlib import Path
import datetime

from lib.bot import Bot


class Sev(Cog):
    def __init__(self, bot):
        self.enabled = False
        self.bot: Bot = bot
        self.sev_id = 139418002369019905  # sev
        # openai initialization
        self.role_description = Path("res/sev_prompt.txt") \
            .read_text() \
            .replace("\n", " ") \
            .strip()

    def remove_mentions(self, message: Message) -> str:
        """Removes mentions from a message"""
        message_without_mentions = message.content
        for user in message.mentions:
            message_without_mentions = message_without_mentions.replace(user.mention, "")
        for role in message.role_mentions:
            message_without_mentions = message_without_mentions.replace(role.mention, "")
        return message_without_mentions

    async def send_message_as_sev(self, message: str, channel: TextChannel, guild: Guild):
        sev = discord.utils.get(self.bot.get_all_members(), id=self.sev_id)
        nick: str = sev.nick if isinstance(sev, discord.Member) and sev.nick is not None else sev.display_name
        guild_webhooks: list[discord.Webhook] = await guild.webhooks()
        webhooks_filtered: list[discord.Webhook] = [w for w in guild_webhooks if str(channel.id) in w.name]
        if not webhooks_filtered:
            webhook: discord.Webhook = await channel.create_webhook(name=f'say-cmd-hook-{channel.id}')
        else:
            webhook: discord.Webhook = webhooks_filtered[0]
        await webhook.send(content=message, username=nick, avatar_url=sev.display_avatar.url)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Sev ist wieder für uns da!")

    @Cog.listener()
    async def on_message(self, message: Message):
        if not self.enabled:
            return
        if not any(user.id == self.sev_id for user in message.mentions):
            return
        message_without_mentions = f"{message.author.display_name}: {self.remove_mentions(message)}"
        messages_before = filter(lambda m: len(m.content) <= 100,
                                 await message.channel.history(limit=20, oldest_first=False).flatten())
        messages_before = [f"[{str(m.created_at)}] {m.author.display_name}: {self.remove_mentions(m)}" for m in
                           messages_before]
        messages_before = [m for m in messages_before if m != ""]
        messages_before.reverse()
        messages_before_acc = "\n".join(messages_before)
        message_without_mentions = f"{messages_before_acc}\n\n{message_without_mentions}"
        try:
            bot_msg, costs = llm.claude(self.bot).get_response(self.role_description, message_without_mentions)
            bot_msg = bot_msg.strip()
            bot_msg = f"{bot_msg}\n\n||Diese Nachricht hat {costs}ct gekostet||"
            # remove the sev: prefix
            sev = discord.utils.get(self.bot.get_all_members(), id=self.sev_id)
            bot_msg = bot_msg.replace("sev:", "").replace("Sev:", "").replace(f"{sev.display_name}:", "")
        except Exception as e:
            print(e)
            return
        await self.send_message_as_sev(message=bot_msg,
                                       channel=message.channel,
                                       guild=message.guild)

    @command()
    @commands.has_permissions(administrator=True)
    async def toggle_sev(self, ctx: Context):
        """toggles the sev bot"""
        # check the current usage for today
        self.enabled = not self.enabled
        info_message = f"Sev is now {'enabled' if self.enabled else 'disabled'}."
        await ctx.send(info_message)


def setup(bot):
    bot.add_cog(Sev(bot))
