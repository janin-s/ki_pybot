
from discord import Embed, Colour
from discord.ext.commands import *
import os, binascii

from lib.utils import true_random_int


class Random(Cog):

    def __init__(self, bot):
        self.bot = bot

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
        
    @command(aliases=['flag'])
    async def flag(self, ctx):
        """ Generate yourself a flag """
        # To remember our fallen brothers & adored tutors in the battle of the flags. 
        # Never forget the brave soldiers at the front of the red flags.
        # Acta est fabula, plaudite!
        await ctx.send(f"flag\{{binascii.b2a_hex(os.urandom(18))}\}")

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


def setup(bot):
    bot.add_cog(Random(bot))
