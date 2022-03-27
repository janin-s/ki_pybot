import datetime
import os.path

import json
import requests

from discord import Embed, Colour, File
from discord.ext.commands import Cog, command

from lib.covid_utils import incidence_image


class Covid(Cog):
    quote_age = (0.0, datetime.datetime.min)
    inzidenz_img_age = datetime.datetime.min

    def __init__(self, bot):
        # setup folder for
        if not os.path.exists('./data/other'):
            os.mkdir('./data/other')

        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('covid')

    @command(aliases=['corona', 'trauer'])
    async def ampel(self, ctx):
        """information about the current corona virus situation in bavaria"""
        url = requests.get('https://corona-ampel-bayern.de/data/data.json')
        data = json.loads(url.text)

        embed = Embed(title='Corona Info')

        if data['officialState'] == 'red':
            embed.add_field(name='Aktuelle Warnstufe', value='ROT', inline=False)
            embed.colour = Colour.from_rgb(255, 0, 0)
            embed.set_thumbnail(url='https://www.tigerlilly.de/wp-content/uploads/2019/01/rot.jpg')
        elif data['officialState'] == 'yellow':
            embed.add_field(name='Aktuelle Warnstufe', value='GELB', inline=False)
            embed.colour = Colour.from_rgb(255, 255, 0)
            embed.set_thumbnail(url='https://www.juedische-allgemeine.de/wp-content/uploads/2018/10/25648-1160x580-c'
                                    '-default.jpg')
        else:
            embed.add_field(name='Aktuelle Warnstufe', value='GRüN', inline=False)
            embed.colour = Colour.from_rgb(0, 255, 0)
            embed.set_thumbnail(url='https://dm0qx8t0i9gc9.cloudfront.net/thumbnails/video/GTYSdDW/brush-paints-a'
                                    '-green-screen_bnql9tru_thumbnail-1080_01.png')
        embed.add_field(name='Inzidenz', value=str(round(float(data['stateInfo']['weekIncidence']), 2)))
        embed.add_field(name='Hospitalization (Last 7 Days):', value=data['hospitalizationLast7Days'])
        embed.add_field(name='Aktuelle Intensivpatient:innen:', value=data['currentIntensiveCarePatients'])
        embed.add_field(name='Prozent Gelb / Prozent Rot:', value=f"{data['yellowPercent']}% / {data['redPercent']}%")
        embed.add_field(name='Impfquote:', value='{:.2f}%'.format(self.get_impfquote()))
        embed.add_field(name='Für entsprechende Regeln siehe:', value='https://corona-ampel-bayern.de/', inline=False)
        embed.timestamp = datetime.datetime.fromisoformat(data['lastUpdate'][:-1])

        await ctx.send(embed=embed)

    @command(aliases=['inzidenzen', 'incidence'])
    async def inzidenz(self, ctx):
        """corona virus inzidenz for selected districts visualized"""
        path = './data/other/incidence.png'
        if self.inzidenz_img_age.date() == datetime.datetime.today().date():
            print('sent inzidenz without api request or image generating')
            await ctx.send(file=File(path))
            return

        incidence_image(path)

        self.inzidenz_img_age = datetime.datetime.now()
        await ctx.send(file=File(path))

    @command()
    async def impfe(self, ctx):
        """current percentage of idiots who are not vaccinated"""
        quote = self.get_impfquote()
        # jaja kinder und vorerkrankungen bla bla aber eh nur dummer joke also hdm
        await ctx.send('Aktuell sind {:.2f}% der Deutschen ungeimpfte Idioten :('.format(100. - quote))

    def get_impfquote(self):
        if datetime.datetime.now() - self.quote_age[1] > datetime.timedelta(hours=6):
            data_complete = json.loads(requests.get('https://rki-vaccination-data.vercel.app/api/v2').text)
            try:
                de = None
                data = data_complete['data']
                for d in data:
                    if d['name'] == 'Deutschland':
                        de = d
                if de is None:
                    return self.quote_age[0]
                quote_once = float(de['vaccinatedAtLeastOnce']['quote'])
                self.quote_age = (quote_once, datetime.datetime.now())
                return quote_once
            except KeyError:
                return self.quote_age[0]
        else:
            return self.quote_age[0]


def setup(bot):
    bot.add_cog(Covid(bot))
