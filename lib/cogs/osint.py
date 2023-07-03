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
import re
from bs4 import BeautifulSoup


class Osint(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.proxy_url = "http://localhost:8191/v1"
        # use flaresolverr to bypass cloudflare
        self.url = "https://search.0t.rocks/records"

    def send_request(self, email: str):
        res = requests.post(url=self.proxy_url, json={
            "cmd": "request.get",
            "url": f"{self.url}?emails={email}&exact=true",
            "maxTimeout": 60000
        }, headers={
            "content-type": "application/json"
        })
        return res

    def generate_infos(self, email):
        res = self.send_request(email)
        if res.status_code != 200:
            return None
        print(f"Got the following response body: {res.json()}")
        html = res.json()["solution"]["response"]
        soup = BeautifulSoup(html, 'html.parser')
        records = soup.find_all('div', {'class': 'record'})
        results = []
        for record in records:
            dd_elements = record.find_all('dd')
            result = []
            for dd in dd_elements:
                result.append(dd.text)
            results.append(result)
        return results

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("OSINT enabled!")

    @command()
    async def osint(self, ctx: Context, email=None):
        """sends you a ticket"""
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not email or not re.fullmatch(email_regex, email):
            await ctx.send("`!osint max@gmail.com`")
            return
        results = self.generate_infos(email)
        if not results:
            await ctx.send("Konnte keine Daten finden. :(")
            return
        with open("/tmp/osint.txt", "w") as f:
            for result in results:
                for line in result:
                    f.write(line + "\n")
                f.write("\n")
        await ctx.send(f"Infos zu `{email}`:", file=discord.File("/tmp/osint.txt"))


def setup(bot):
    bot.add_cog(Osint(bot))
