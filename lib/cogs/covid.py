import datetime
import os.path

import json
import requests

from discord import Embed, Colour, File
from discord.ext.commands import *
import matplotlib.pyplot as plt


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
        base_url = 'https://api.corona-zahlen.org'
        if self.inzidenz_img_age.date() == datetime.datetime.today().date():
            print('sent inzidenz without api request or image generating')
            await ctx.send(file=File(path))
            return

        # total
        germany_incidence = get_from_api(f'{base_url}/germany', ['weekIncidence'])
        germany_last_incidence = get_from_api(f'{base_url}/germany/history/incidence/2', ['data', 0, 'weekIncidence'])

        # bavaria
        bavaria_incidence = get_from_api(f'{base_url}/states', ['data', 'BY', 'weekIncidence'])
        bavaria_last_incidence = get_from_api(f'{base_url}/states/history/incidence/2',
                                              ['data', 'BY', 'history', 0, 'weekIncidence'])

        # districts
        districts = ['09184', '09178', '09162', '09175', '09274', '05112']
        data = json.loads(requests.get(f'{base_url}/districts/').text)
        incidences, names, incidences_before = {}, {}, {}
        for district in districts:
            try:
                district_data = data['data'][district]
                incidences[district] = district_data['weekIncidence']
                names[district] = district_data['county']
            except KeyError:
                districts.remove(district)
                print(f'couldn\'t find district {district} (or JSON malformed)')
        # districts change
        data_before = json.loads(requests.get(f'{base_url}/districts/history/incidence/2').text)
        for district in districts:
            incidences_before[district] = \
                get_from_dict(data_before, ['data', district, 'history', 0, 'weekIncidence'])

        create_incidence_image(bavaria_incidence, bavaria_last_incidence, data, germany_incidence,
                               germany_last_incidence, incidences, incidences_before, names, path)
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


def get_from_api(url, keys):
    val = json.loads(requests.get(url).text)
    try:
        for key in keys:
            val = val[key]
        return val
    except KeyError:
        return 0


def get_from_dict(data, keys):
    val = data
    try:
        for key in keys:
            val = val[key]
        return val
    except KeyError:
        return None


def create_incidence_image(bavaria_incidence, bavaria_last_incidence, data, germany_incidence,
                           germany_last_incidence, incidences, incidences_before, names, path):
    plt.figure(figsize=(8, 5))
    sorted_incidences = sorted(incidences.items(), key=lambda x: x[1])[::-1]
    container = plt.bar(
        list(names[a] for a, _ in sorted_incidences) + ['Deutschland\n(gesamt)', 'Bayern\n(gesamt)'],
        list(b for _, b in sorted_incidences) + [germany_incidence, bavaria_incidence],
        align='center', width=0.3, color='#8ec07c')
    plt.axhline(y=1000, linewidth=1, color='red')
    plt.bar_label(container=container, labels=list(
        format_incidence_change(v, incidences_before[k]) for k, v in sorted_incidences)
                                              + [format_incidence_change(germany_incidence,
                                                                         germany_last_incidence),
                                                 format_incidence_change(bavaria_incidence,
                                                                         bavaria_last_incidence)])
    plt.title('Wöchentliche Inzidenzen')
    plt.xlabel('Zuletzt aktualisert: ' + datetime.datetime.fromisoformat(data['meta']['lastUpdate'][:-1])
               .strftime('%d.%m. %H:%M') + '\n(Veränderungen: täglich)',
               labelpad=15)
    plt.ylabel('')
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, y1, y2 + 110))
    plt.subplots_adjust(bottom=-1)
    plt.tight_layout()
    plt.savefig(path)


def format_incidence_change(incidence, incidence_before):
    if incidence is None or incidence == 0:
        return 'N/A'
    s = '{:.2f}'.format(incidence) + '\n('
    if incidence_before is None or incidence_before == 0:
        return s + 'N/A)'
    ratio = incidence / incidence_before
    if ratio > 1.0:
        s += '+'
    s += '{:.2%}'.format(ratio - 1.0) + ')'
    return s


def setup(bot):
    bot.add_cog(Covid(bot))
