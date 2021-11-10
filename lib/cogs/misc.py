import datetime

import json
import requests
from discord import Embed, Colour
from discord.ext.commands import *

from lib.db import db


class Misc(Cog):
    quote_age = (0.0, datetime.datetime.min)

    def __init__(self, bot):
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


def setup(bot):
    bot.add_cog(Misc(bot))
