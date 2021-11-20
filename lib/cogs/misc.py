import datetime

import tweepy as tw
import json
import requests
import random
from discord import Embed, Colour, File
from discord.ext.commands import *
from tweepy import Response
import matplotlib.pyplot as plt

from lib.db import db


class Misc(Cog):
    quote_age = (0.0, datetime.datetime.min)
    api_key = ''
    api_secret = ''
    bearer_token = ''
    api = None
    tweets = None

    def __init__(self, bot):
        with open(r"./data/keys/twitter_api_key", "r", encoding="utf-8") as kf:
            self.api_key = kf.read()
        with open(r"./data/keys/twitter_secret_key", "r", encoding="utf-8") as skf:
            self.api_secret = skf.read()
        with open(r"./data/keys/bearer_token", "r", encoding="utf-8") as bf:
            self.bearer_token = bf.read()
        self.client = tw.Client(bearer_token=self.bearer_token,
                                consumer_key=self.api_key,
                                consumer_secret=self.api_secret,
                                wait_on_rate_limit=True,
                                return_type=Response)

        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")

    @command()
    async def amongus(self, ctx):
        """switches channel limit for Pannekecke from infinity to 99 and back"""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
        else:
            await ctx.send("not connected to a voice channel!")
            return
        current_limit = channel.user_limit
        if current_limit == 0:
            await channel.edit(user_limit=99)
            await ctx.send("among us modus (user anzahl sichtbar) aktiviert")
        else:
            await channel.edit(user_limit=0)
            await ctx.send("among us modus (user anzahl sichtbar) deaktiviert")

    @command()
    async def zitat(self, ctx, length=1):
        """!zitat [x]; zitiert die letze[n x] Nachricht[en] und speichert sie in Relikte"""
        zitat: str = ""
        message_list = []
        async for message in ctx.channel.history(limit=length + 1):
            message_list.append(message)
        message_list.reverse()
        for m in message_list:
            zitat += m.author.display_name + ": \"" + m.content + "\"\n"
        quote_channel_id = db.field("SELECT quote_channel FROM server_info WHERE guild_id = ?", ctx.guild)
        if quote_channel_id is None:
            quote_channel_id = ctx.channel.id
        quote_channel = await self.bot.fetch_channel(quote_channel_id)
        await quote_channel.send(zitat)

    @command(aliases=['corona', 'trauer'])
    async def ampel(self, ctx):
        url = requests.get('https://corona-ampel-bayern.de/data/data.json')
        text = url.text
        data = json.loads(text)

        embed = Embed(title='Corona Info')

        if data['officialState'] == "red":
            embed.add_field(name="Aktuelle Warnstufe", value='ROT', inline=False)
            embed.colour = Colour.from_rgb(255, 0, 0)
            embed.set_thumbnail(url='https://www.tigerlilly.de/wp-content/uploads/2019/01/rot.jpg')
        elif data['officialState'] == "yellow":
            embed.add_field(name="Aktuelle Warnstufe", value='GELB', inline=False)
            embed.colour = Colour.from_rgb(255, 255, 0)
            embed.set_thumbnail(url='https://www.juedische-allgemeine.de/wp-content/uploads/2018/10/25648-1160x580-c'
                                    '-default.jpg')
        else:
            embed.add_field(name="Aktuelle Warnstufe", value='GRüN', inline=False)
            embed.colour = Colour.from_rgb(0, 255, 0)
            embed.set_thumbnail(url='https://dm0qx8t0i9gc9.cloudfront.net/thumbnails/video/GTYSdDW/brush-paints-a'
                                    '-green-screen_bnql9tru_thumbnail-1080_01.png')

        embed.add_field(name="Hospitalization (Last 7 Days):", value=data['hospitalizationLast7Days'])
        embed.add_field(name='Aktuelle Intensivpatient:innen:', value=data['currentIntensiveCarePatients'])
        embed.add_field(name='Prozent Gelb / Prozent Rot:', value=f'{data["yellowPercent"]}% / {data["redPercent"]}%')
        embed.add_field(name='Impfquote:', value="{:.2f}%".format(self.get_impfquote()))
        embed.add_field(name='Für entsprechende Regeln siehe:', value="https://corona-ampel-bayern.de/", inline=False)
        embed.timestamp = datetime.datetime.fromisoformat(data["lastUpdate"][:-1])

        await ctx.send(embed=embed)

    @command(aliases=['inzidenzen'])
    async def inzidenz(self, ctx):
        # total
        germany_incidence = json.loads(requests.get("https://api.corona-zahlen.org/germany").text)["weekIncidence"]
        germany_last_incidence = json.loads(requests.get("https://api.corona-zahlen.org/germany/history/incidence/2")
                                            .text)["data"][0]["weekIncidence"]
        # districts
        districts = ["09184", "09178", "09162", "09175", "09274", "05112"]
        url = requests.get('https://api.corona-zahlen.org/districts/')
        data = json.loads(url.text)
        incidences = {}
        names = {}
        for district in districts:
            district_data = data["data"][district]
            incidences[district] = district_data["weekIncidence"]
            names[district] = district_data["county"]
        # before
        url = requests.get('https://api.corona-zahlen.org/districts/history/incidence/2')
        data_before = json.loads(url.text)
        incidences_before = {}
        for district in districts:
            district_data = data_before["data"][district]
            incidences_before[district] = district_data["history"][0]["weekIncidence"]
        # sort by incidence and create chart
        plt.figure(figsize=(8, 5))
        sorted_incidences = sorted(incidences.items(), key=lambda x: x[1])[::-1]
        container = plt.bar(
            list(names[a] for a, _ in sorted_incidences) + ["Deutschland\n(gesamt)"],
            list(b for _, b in sorted_incidences) + [germany_incidence],
                            align="center", width=0.3, color="#8ec07c")
        plt.axhline(y=1000, linewidth=1, color='red')
        plt.bar_label(container=container, labels=list(
            self.format_incidence_change(v, incidences_before[k]) for k, v in sorted_incidences)
                      + [self.format_incidence_change(germany_incidence, germany_last_incidence)])
        plt.title("Wöchentliche Inzidenzen")
        plt.xlabel("Zuletzt aktualisert: " + datetime.datetime.fromisoformat(data["meta"]["lastUpdate"][:-1])
                   .strftime("%d.%m. %H:%M") + "\n(Veränderungen: täglich)",
                   labelpad=15)
        plt.ylabel("")
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, y1, y2 + 110))
        plt.subplots_adjust(bottom=-1)
        plt.tight_layout()
        path = "/tmp/incidence.png"
        plt.savefig(path)
        await ctx.send(file=File(path))

    def format_incidence_change(self, incidence, incidence_before):
        s = "{:.2f}".format(incidence) + "\n("
        ratio = incidence / incidence_before
        if ratio > 1.0:
            s += "+"
        s += "{:.2%}".format(ratio - 1.0) + ")"
        return s

    @command()
    async def impfe(self, ctx):
        quote = self.get_impfquote()
        # jaja kinder und vorerkrankungen bla bla aber eh nur dummer joke also hdm
        await ctx.send("Aktuell sind {:.2f}% der Deutschen ungeimpfte Idioten :(".format(100. - quote))

    def get_impfquote(self):
        if datetime.datetime.now() - self.quote_age[1] > datetime.timedelta(hours=6):
            print('getting new quote')
            url = requests.get('https://rki-vaccination-data.vercel.app/api/v2')
            text = url.text
            data_complete = json.loads(text)
            data = data_complete['data']
            for d in data:
                if d['name'] == 'Deutschland':
                    de = d
            quote_once = float(de['vaccinatedAtLeastOnce']['quote'])
            self.quote_age = (quote_once, datetime.datetime.now())
            return quote_once
        else:
            return self.quote_age[0]

    @command(aliases=['mülltake', 'shittake'])
    async def trashtake(self, ctx):
        id = 809188392089092097
        # if list empty get new tweets
        if self.tweets is None or len(self.tweets) == 0:
            response: tw.Response = self.client.get_users_tweets(id=id, exclude=['replies', 'retweets'],
                                                                 max_results=100)
            self.tweets = response.data

        # get first tweet in list
        tweet = self.tweets[0]
        # remove first tweet from list
        self.tweets = self.tweets[1:]
        await ctx.send(tweet)


def setup(bot):
    bot.add_cog(Misc(bot))
