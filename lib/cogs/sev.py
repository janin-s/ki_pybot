import discord
from discord.ext import commands
from discord.ext.commands import Cog, command, Context
from discord.message import Message
from discord.channel import TextChannel
from discord.guild import Guild
import numpy as np
import openai, openai.api_requestor
from pathlib import Path
import datetime

from lib.bot import Bot


class Sev(Cog):
    def __init__(self, bot):
        self.enabled = False
        self.bot: Bot = bot
        self.sev_id = 139418002369019905  # sev
        # openai initialization
        openai.organization = self.bot.config.openai_org_id
        openai.api_key = self.bot.config.openai_api_key
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

    def generate_response(self, message: str) -> str:
        """Generates a response from the given message"""
        print(f"Generating response for message: {message}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": self.role_description
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            n=1,
            max_tokens=256
        )
        return response.choices[0].message.content

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
                                 await message.channel.history(limit=10, oldest_first=False).flatten())
        messages_before = [f"{m.author.display_name}: {self.remove_mentions(m)}" for m in messages_before]
        messages_before = [m for m in messages_before if m != ""][:5]
        messages_before.reverse()
        messages_before_acc = "\n".join(messages_before)
        message_without_mentions = f"{messages_before_acc}\n\n{message_without_mentions}"
        try:
            bot_msg: str = self.generate_response(message=message_without_mentions)
            bot_msg = bot_msg.strip().lstrip("sev:")
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
        requestor = openai.api_requestor.APIRequestor()
        start_date = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.date.today().strftime('%Y-%m-%d')
        res = requestor.request("GET", f"/dashboard/billing/usage?end_date={end_date}&start_date={start_date}")
        costs = "{:.2f}".format(float(res[0].data["total_usage"]) / 100)
        self.enabled = not self.enabled
        info_message = f"Sev is now {'enabled' if self.enabled else 'disabled'} and has been used for {costs}€ in the last week."
        await ctx.send(info_message)


def setup(bot):
    bot.add_cog(Sev(bot))
