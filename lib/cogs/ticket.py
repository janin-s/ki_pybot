import discord
from discord.ext import commands
from discord.ext.commands import Cog, command, Context
from discord.message import Message
from discord.channel import TextChannel
from discord.guild import Guild
import requests
from pathlib import Path
from datetime import datetime, timedelta
import locale
from lib.bot import Bot


class Ticket(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.url = "https://api.brevo.com/v3/smtp/email"
        self.api_key = self.bot.config.brevo_api_key
        self.html_template = Path("res/ticket.txt").read_text()

    def send_mail(self, sender_mail: str, receiver_mail: str, subject: str, html_content: str):
        res = requests.post(url=self.url, headers={
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }, json={
            "sender": {
                "email": sender_mail,
                "name": sender_mail
            },
            "to": [
                {
                    "email": receiver_mail,
                    "name": receiver_mail
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        })
        return res

    async def send_fake_ticket(self, full_name, email):
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%d. %B %Y")
        first_month_day = datetime.now().replace(day=1).strftime("%d. %B %Y")
        locale.setlocale(locale.LC_TIME, '')
        content = self.html_template \
            .replace("%NAME%", full_name) \
            .replace("%DATE%", yesterday_date) \
            .replace("%START%", first_month_day)
        res = self.send_mail("abocenter@mvg.de",
                             email,
                             "MVG Kundenportal - Bestellbestätigung",
                             content)
        return res.json()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Notfallticket enabled!")

    @command()
    async def ticket(self, ctx: Context):
        await ctx.send("`!ticket Max Mustermann max@mustermann.de`")

    @command()
    async def ticket(self, ctx: Context, first_name, last_name, email):
        """sends you a ticket"""
        # check the current usage for today
        res = await self.send_fake_ticket(f"{first_name} {last_name}", email)
        await ctx.send(f"Ticket sent to {email} with status {res['status']}")


def setup(bot):
    bot.add_cog(Ticket(bot))
