import json
import random

import requests
from discord import Embed, File, TextChannel, Message
from discord.ext.commands import *
from apscheduler.triggers.cron import CronTrigger

from lib.db import db
from datetime import datetime, timedelta

from lib.covid_utils import incidence_image


class DailyInfos(Cog):
    def __init__(self, bot):
        # load api keys
        with open(r"./data/keys/news_api_key", "r", encoding="utf-8") as nk:
            self.NEWS_API_KEY = nk.read()
        with open(r"./data/keys/weather_api_key", "r", encoding="utf-8") as wk:
            self.WEATHER_API_KEY = wk.read()

        self.bot = bot
        bot.scheduler.add_job(self.print_daily_infos, CronTrigger(hour=2))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("dailyinfos")

    @command()
    @has_permissions(administrator=True)
    async def print_daily_infos(self, ctx=None):
        guilds = db.records('SELECT guild_id, name, reminder_channel, quote_channel FROM server_info')
        for _, name, rem_channel, quote_channel in guilds:
            await self.print_daily_infos_for_guild(name, rem_channel, quote_channel)

    async def print_daily_infos_for_guild(self, name: str, main_channel_id: int, quote_channel_id: int):
        main_channel: TextChannel = await self.bot.fetch_channel(main_channel_id)
        main_embed: Embed = Embed(title='Daily Updates!', description='Guten Morgen :)')
        inzidenz_file = get_incidence_image_embed()
        main_embed.set_image(url='attachment://incidence.png')
        await main_channel.send(file=inzidenz_file, embed=main_embed)

        relikte_embed = await self.get_relikte_throwback_embed(quote_channel_id)
        weather_embed = get_weather_info_embed(self.WEATHER_API_KEY)
        news_embed = get_news_embed(self.NEWS_API_KEY)
        embeds = [relikte_embed, weather_embed, news_embed]

        for e in embeds:
            if e is not None:
                await main_channel.send(embed=e)

    async def get_relikte_throwback_embed(self, quote_channel_id) -> Embed | None:
        channel: TextChannel = await self.bot.fetch_channel(quote_channel_id)
        if channel is None:
            return
        today = datetime.today()
        # TODO handle leap year, where there is no history
        old_messages = []
        for date in [today.replace(year=today.year - i) for i in range(1, 5)]:
        # for date in [today - timedelta(days=i) for i in range(1, 5)]:
            history = channel.history(before=date + timedelta(days=1), after=date)
            async for m in history:
                old_messages.append(m)

        if len(old_messages) == 0:
            return None

        old_message: Message = random.choice(old_messages)
        year = datetime.today().year - old_message.created_at.year

        info_message = f"{old_message.author.display_name} {year} year{'' if year == 1 else 's'} ago today:"

        if old_message.attachments is None or len(old_message.attachments) == 0:
            embed: Embed = Embed(title=info_message, description=old_message.content)
            return embed
        embed: Embed = Embed(title=info_message)
        embed.set_image(url=old_message.attachments[0].url)
        return embed


def get_weather_info_embed(api_key) -> Embed | None:
    LATITUDE = 48.25
    LONGITUDE = 11.65
    api_call = f'https://api.openweathermap.org/data/2.5/onecall?lat={LATITUDE}&lon={LONGITUDE}&exclude=current,' \
               f'minutely,hourly,alerts&units=metric&lang=de&appid={api_key}'
    data = json.loads(requests.get(api_call).text)

    embed: Embed = Embed(title="Wetter in Garching heute:")

    data_today = data['daily'][0]
    embed.add_field(name='Wetter', value=data_today['weather'][0]['description'])
    embed.add_field(name='Temperatur', value=f"{data_today['temp']['day']}°C    "
                                             f"({data_today['temp']['min']}°C - {data_today['temp']['max']}°C)")
    embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{data_today['weather'][0]['icon']}@2x.png")
    return embed


def get_news_embed(api_key) -> Embed | None:
    url = f'https://newsapi.org/v2/top-headlines?sources='
    data_zeit = json.loads(requests.get(f'{url}die-zeit&apiKey={api_key}').text)
    data_spiegel = json.loads(requests.get(f'{url}spiegel-online&apiKey={api_key}').text)
    spiegel_articles = data_spiegel['articles'][:3]
    zeit_articles = \
        list(filter(
            lambda a: not ('Corona-Zahlen' in a['title'] or 'Fotografie' in a['title'] or a['description'] is None),
            data_zeit['articles']))[:3]

    articles = spiegel_articles + zeit_articles

    embed: Embed = Embed(title='Aktuelle Schlagzeilen')
    for article in articles:
        embed.add_field(name=f"{article['title']}",
                        value=f"[{article['source']['name']}]({article['url']})")
    return embed


def get_incidence_image_embed() -> File:
    incidence_image(path='./data/other/incidence.png')
    incidence_image_file = File('./data/other/incidence.png', filename='incidence.png')
    return incidence_image_file


def setup(bot):
    bot.add_cog(DailyInfos(bot))
