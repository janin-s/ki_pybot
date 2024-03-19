import binascii
import os
import time

from discord import Embed, Colour, File
from discord.ext.commands import Cog, command

from lib.bot import Bot
from lib.utils.utils import true_random_int

import requests
import io
import aiohttp

import datetime
import random

from PIL import Image, ImageChops
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Random(Cog):

    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('random')

    @command(aliases=['coin'])
    async def coinflip(self, ctx):
        """ flip a coin """
        # easier but not as cool
        # number = random.randint(0, 1)
        numbers = true_random_int(0, 1, 1)
        if not numbers:
            await ctx.send('something went wrong :(')
            return
        if numbers[0] == 0:
            embed = Embed(title='HEADS', color=0xca9502)
        else:
            embed = Embed(title='TAILS', color=0xca9502)
        await ctx.send(embed=embed)

    @command()
    async def flag(self, ctx):
        """ Generate yourself a flag """
        # To remember our fallen brothers & adored tutors in the battle of the flags.
        # Never forget the brave soldiers at the front of the red flags.
        # Acta est fabula, plaudite!
        await ctx.send('flag{' + str(binascii.b2a_hex(os.urandom(18)).decode()) + '}')

    @command(aliases=['orakel'])
    async def oracle(self, ctx):
        """ ask the oracle """
        # easier but not as cool
        # number = random.randint(0, 1)
        numbers = true_random_int(0, 9, 1)
        if not numbers:
            await ctx.send('something went wrong :(')
            return
        if numbers[0] < 2:
            message = '<:maybe:924429043330338816>'
        elif numbers[0] < 6:
            message = '<:yes:731290826365468755>'
        else:
            message = '<:no:731290826142908550>'
        await ctx.send(message)

    @command(aliases=['würfel'])
    async def dice(self, ctx, amount=1):
        """ throw a dice with !dice, throw multiple (up to 5) with !dice x """
        if amount < 1 or amount > 5:
            amount = 1
        numbers = true_random_int(1, 6, amount)
        if not numbers:
            await ctx.send('something went wrong :(')
            return

        embed = Embed(title=str(numbers)[1:-1].replace(',', ''), color=Colour.from_rgb(255, 255, 255))
        await ctx.send(embed=embed)

    @command()
    async def stäbli(self, ctx):
        """ get the number of visitors in the stäblibad """
        res = requests.get("https://functions.api.ticos-systems.cloud/api/gates/counter?organizationUnitIds=30194",
                           headers={
                               "abp-tenantid": "69"
                           })
        visitors = int(res.json()[0]['personCount'])
        max_visitors = int(res.json()[0]['maxPersonCount'])
        percentage = "{0:.0%}".format(visitors / max_visitors)
        await ctx.send(f"{visitors}/{max_visitors} ({percentage})")

    @command()
    async def fitstar(self, ctx):
        """get the current capacity of fitstar neuried"""

        csv_path = "/home/regular/fitstar/fitstar.csv"
        # get last 24h of the csv file
        with open(csv_path, "rb") as f:
            line_count = 24 * 60
            lines = f.readlines()[-line_count:]
        # get all entries that are not older than 24 hours
        current_timestamp = datetime.datetime.now().timestamp()
        x = []
        y = []
        for line in lines:
            timestamp, percentage = line.decode().strip().split(",")
            if current_timestamp - float(timestamp) < 24 * 60 * 60:
                date = datetime.datetime.fromtimestamp(float(timestamp))
                x.append(date)
                y.append(int(percentage))
        # create a plot
        plt.plot(x, y)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())
        plt.gcf().autofmt_xdate()
        plt.xlabel("time")
        plt.ylabel("percentage")
        plt.title("fitstar neuried capacity")
        plt.savefig("/tmp/fitstar.png")
        plt.close()
        await ctx.send(file=File("/tmp/fitstar.png"))

    @command()
    async def jumpers(self, ctx):
        """get the current number of npcs of jumpers"""
        res = requests.get("https://www.jumpers-fitness.com/club-checkin-number/40/Jumpers.JumpersFitnessTld")
        checked_in = res.json()["countCheckedInCustomer"]
        msg = f"{checked_in} npcs"
        await ctx.send(msg)

    @command()
    async def label(self, ctx, *args):
        """ Generate a label with a given name """
        name = ' '.join(args)
        # Generate a random date in the format YYYY-MM-DD
        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date.today()
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)

        payload = {
            "country": "Germany",
            "name": name,
            "roaster": name,
            "varietals": name,
            "region": name,
            "farm": name,
            "elevation": "1m",
            "doseWeight": 1000,
            "roastingDate": random_date.strftime("%Y-%m-%d"),
            "processing": name,
            "aromatics": name
        }

        try:
            response = requests.post('https://coffee.maxkienitz.com/api/og/biglabel', json=payload)
            response.raise_for_status()
            with open("/tmp/label.png", 'wb') as f:
                f.write(response.content)
            await ctx.send(file=File("/tmp/label.png"))

        except requests.exceptions.RequestException as e:
            await ctx.send(f'An error occurred: {e}')


def setup(bot):
    bot.add_cog(Random(bot))
