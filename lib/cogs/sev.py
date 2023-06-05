import discord
from discord.ext.commands import Cog, command, Context
from discord.message import Message, TextChannel
from discord.guild import Guild
import numpy as np
import openai

from lib.bot import Bot


class Sev(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.sev_id = 139418002369019905  # sev
        # openai initialization
        openai.organization = self.bot.config.openai_org_id
        openai.api_key = self.bot.config.openai_api_key
        self.role_description = "Verhalte dich wie Sev, ein Informatikstudent an der TUM und aktiver Pfadfinder." \
                                "Du bist oft mit Pfadfinderaktivitäten beschäftigt und gibst deinen Freunden wenig " \
                                "Aufmerksamkeit. Deine Antworten sind kurz und umgangssprachlich, meistens in " \
                                "Kleinbuchstaben, oft nur ein paar Worte. " \
                                "Du benutzt häufig Ausdrücke wie 'walla', ':((', 'bruh' und 'rr' (real rap). " \
                                "Deine Diskussionen drehen sich oft um technische Probleme oder politische Themen, " \
                                "und du zeigst offen deine Emotionen, besonders wenn du auf technische " \
                                "Herausforderungen stößt. Bei Beleidigungen antwortest du nicht formal, sondern " \
                                "reagierst mit einem traurigen Smiley oder ähnlichem."

    def generate_response(self, message: str) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": self.role_description,
                    "content": message
                }
            ],
            n=1,
            max_tokens=256
        )
        return completion.choices[0].message

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
        if not any(user.id == self.sev_id for user in message.mentions):
            return
        # Only impersonate sev with a certain probability
        if not np.random.choice(a=[True, False], p=[0.1, 0.9]):
            return
        try:
            bot_msg: str = self.generate_response(message=message.clean_content())
        except Exception as e:
            print(e)
            return
        await self.send_message_as_sev(message=bot_msg,
                                       channel=message.channel,
                                       guild=message.guild)


def setup(bot):
    bot.add_cog(Sev(bot))
