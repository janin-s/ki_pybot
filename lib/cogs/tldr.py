import string

import discord
from discord.ext import commands
from discord.ext.commands import Cog, command, Context
from discord.message import Message
from discord.channel import TextChannel
from discord.guild import Guild
from discord.ext.commands import BucketType
import numpy as np
import openai, openai.api_requestor
from pathlib import Path
import datetime

from lib.bot import Bot


class Tldr(Cog):
    def __init__(self, bot):
        self.enabled = False
        self.bot: Bot = bot
        # openai initialization
        openai.organization = self.bot.config.openai_org_id
        openai.api_key = self.bot.config.openai_api_key
        self.role_description = Path("res/tldr_prompt.txt") \
            .read_text() \
            .replace("\n", " ") \
            .strip()

    async def get_tldr(self, channel: TextChannel):
        # Step 1: Fetch last 250 messages
        history = await channel.history(limit=250).flatten()

        # Step 2: Draw 25 messages with a higher probability for longer ones
        weights = np.array([len(m.content) for m in history])
        weights = weights / np.sum(weights)  # Normalize weights
        selected_messages = np.random.choice(history, size=50, p=weights, replace=False)

        # Step 3: Remove words with <= 3 letters and all punctuations
        filtered_messages = []
        for m in selected_messages:
            filtered_content = ' '.join(
                word for word in m.content.translate(str.maketrans('', '', string.punctuation)).split() if
                len(word) > 3)
            filtered_messages.append(f"{m.author.display_name}: {filtered_content}")

        # Step 4: Pass the filtered messages to the openai API and generate a short summary
        message_string = '\n'.join(filtered_messages)
        print(f"Generating TL;DR for: {message_string[:100]}...")  # Print a short preview for debugging

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": self.role_description
                },
                {
                    "role": "user",
                    "content": message_string
                }
            ],
            n=1,
            max_tokens=256
        )
        tldr = response.choices[0].message.content
        costs = response.usage.prompt_tokens * 3 + response.usage.completion_tokens * 6
        costs = "{:.2f}".format(costs / 1000)
        return tldr, costs

    @command()
    @commands.cooldown(1, 30 * 60, commands.BucketType.guild)
    async def tldr(self, ctx: Context):
        """Generates a TL;DR summary of the recent discussion in the channel"""
        if self.enabled:
            try:
                await ctx.send("Lese die letzten 250 Nachrichten...")
                tldr, costs = await self.get_tldr(ctx.channel)
                await ctx.send(f"**TLDR der letzten 250 Nachrichten**:\n{tldr}\n\n||Diese Nachricht hat {costs}ct gekostet||")
            except Exception as e:
                print(e)
                await ctx.send("An error occurred while generating the TLDR.")

    @command()
    @commands.has_permissions(administrator=True)
    async def toggle_tldr(self, ctx: Context):
        """toggles the TL;DR generation"""
        self.enabled = not self.enabled
        info_message = f"TLDR is now {'enabled' if self.enabled else 'disabled'}."
        await ctx.send(info_message)


def setup(bot):
    bot.add_cog(Tldr(bot))
