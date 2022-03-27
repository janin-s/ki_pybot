import json
import random

import requests
from discord import Embed, File, TextChannel, Message
from discord.ext.commands import Cog, has_permissions, command
from apscheduler.triggers.cron import CronTrigger

from lib.db import db
from datetime import datetime, timedelta

from lib.covid_utils import incidence_image


class DailyInfos(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.NEWS_API_KEY = self.bot.config.news_api_key
        self.WEATHER_API_KEY = self.bot.config.weather_api_key
        bot.scheduler.add_job(self.print_daily_infos, CronTrigger(hour=8))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("dailyinfos")

    @command()
    @has_permissions(administrator=True)
    async def daily_info(self, ctx):
        """command for triggering the daily info post for current guild"""
        guild_id = ctx.guild.id
        guild = db.record('SELECT name, reminder_channel, quote_channel FROM server_info WHERE guild_id = ?', guild_id)
        if guild is None:
            return
        name, rem_channel, quote_channel = guild
        await self.print_daily_infos_for_guild(name, rem_channel, quote_channel)

    async def print_daily_infos(self):
        """prints daily infos for all guilds"""
        guilds = db.records('SELECT name, reminder_channel, quote_channel FROM server_info')
        for name, rem_channel, quote_channel in guilds:
            await self.print_daily_infos_for_guild(name, rem_channel, quote_channel)

    async def print_daily_infos_for_guild(self, name: str, main_channel_id: int, quote_channel_id: int):
        """prints daily info for one guild"""
        main_channel: TextChannel = await self.bot.fetch_channel(main_channel_id)
        quote_channel: TextChannel = await self.bot.fetch_channel(quote_channel_id)

        main_embed: Embed = Embed(title=f'Guten Morgen {name}')
        inzidenz_file = get_incidence_image_file()
        main_embed.set_image(url='attachment://incidence.png')
        await main_channel.send(file=inzidenz_file, embed=main_embed)

        relikte_embed = await get_relikte_throwback_embed(quote_channel)
        weather_embed = get_weather_info_embed(self.WEATHER_API_KEY)
        news_embed = get_news_embed(self.NEWS_API_KEY)
        embeds = [relikte_embed, weather_embed, news_embed]
        for e in embeds:
            if e is not None:
                await main_channel.send(embed=e)


async def get_relikte_throwback_embed(channel: TextChannel) -> Embed | None:
    """returns an Embed containing a throwback from relikte x years ago on current date"""
    if channel is None:
        return
    today = datetime.today()
    # TODO handle leap year, where there is no history
    old_messages = []
    for date in [today.replace(year=today.year - i) for i in range(1, 5)]:
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
    """returns an Embed containing Weather information for Garching"""
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
    """returns an Embed containg current news headline"""
    url = f'https://newsapi.org/v2/top-headlines?sources='
    data_zeit = json.loads(requests.get(f'{url}die-zeit&apiKey={api_key}').text)
    # data_spiegel = json.loads(requests.get(f'{url}spiegel-online&apiKey={api_key}').text)
    # spiegel_articles = data_spiegel['articles'][:3]

    # filter out unwanted entries in the Zeit data
    articles = filter_articles(data_zeit)[:6]

    embed: Embed = Embed(title='Aktuelle Schlagzeilen')
    for article in articles:
        embed.add_field(name=f"{article['title']}",
                        value=f"[{article['source']['name']}]({article['url']})")
    return embed


def filter_articles(data):
    keywords = ['Corona-Zahlen', 'Fotografie', 'Basketball', 'Fußball', 'Tennis']
    return list(filter(lambda a: not (any(keyword in a['title'] for keyword in keywords)), data['articles']))


def get_incidence_image_file() -> File:
    """returns the incidence image as a discord File"""
    incidence_image(path='./data/other/incidence.png')
    incidence_image_file = File('./data/other/incidence.png', filename='incidence.png')
    return incidence_image_file


def setup(bot):
    bot.add_cog(DailyInfos(bot))
