import fileinput
import random

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', case_insensitive=True)
shot_counter = 0


@bot.event
async def on_ready():
    print(f'{bot.user} ist online')
    await bot.change_presence(activity=discord.Game('Exmatrikulation kickt'), status=discord.Status.online)


@bot.event
async def on_command_error(ctx, error, force=False):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('KI dummdumm :(')
    else:
        await ctx.send("KI nix verstehi ._.")


@bot.command()
async def clear(ctx, amount=1):
    """Lösche die übergebene Anzahl an Messages (default == 1) mit !clear {amount}*"""
    if ctx.channel.id == 705427122151227442:
        await ctx.channel.purge(limit=1)
        await ctx.send('Pseudohistorie wird hier nicht geduldet!', delete_after=60)
    else:
        await ctx.channel.purge(limit=amount + 1)


@bot.command()
async def event(ctx, *, event):
    """Setze ein neues Event mit !event {event}"""
    await ctx.send(f'Current event changed to {event}')
    await bot.change_presence(activity=discord.Game(f'{event}'), status=discord.Status.online)


@bot.command(aliases=["rip", "suizid", "lost"])
async def shot(ctx, *, command=None):
    """Erhöht den Shot-Counter um 1"""
    if ctx.message.author.id == 388061626131283968 or ctx.message.author.id == 295927454562779139:
        if command == "reset":
            newcount = await persistent_counter("resetAll")
        else:
            newcount = await persistent_counter()
        await ctx.send(f'Shot-Counter: {newcount}')
    else:
        await ctx.send('Jonas haut dich <:knast:731290033046159460>', delete_after=60)


async def persistent_counter(caller="all"):
    # premium function
    # hilfsfunktion für shotcounter, wenn ohne argument globaler shared counter
    # evtl in Zukunft für persönliche Counter nutzbar: user-ID als parameter String

    # data stored like this: 'userid:shotcount'
    # shared counter with id 'all'

    if caller == "resetAll":
        for line in fileinput.input(r"data", inplace=True):
            if line.__contains__("all"):
                newline = "all:0"
                print(newline.strip())
            else:
                print(line.strip())
        fileinput.close()
        return 0
    else:
        found = False
        number: int = 0
        print("looking for caller " + caller)
        for line in fileinput.input(r"data", inplace=True):
            if line.__contains__(caller):
                found = True
                try:
                    number = int(line.split(':').__getitem__(1))
                except ValueError:
                    number = 0
                number = number + 1
                newline = caller + ":" + str(number)
                print(newline.strip())
            else:
                print(line.strip())
        fileinput.close()
        if not found:
            data = open(r"data", "a")
            data.write(caller + ":0")
            return -1
        return number



@bot.command(aliases=["hacker"])
async def chrissi(ctx):
    """Chrissi ist gemein und wird deshalb gemobbt"""
    await ctx.send('Chrissi ist so ein Lieber! Sehr nett und sympathisch!', delete_after=7000)


@bot.command(aliases=["frech"])
async def janin(ctx):
    for c in "toll":
        await ctx.send(str(c), delete_after=7000)


@bot.command()
async def gumo(ctx):
    """KI wünscht allen einen guten Morgen"""
    await ctx.send('Ich wünsche allen einen GuMo!')


@bot.command()
async def gumi(ctx):
    """KI wünscht allen einen guten Mittag"""
    await ctx.send('Ich wünsche allen einen GuMi!')


@bot.command()
async def guna(ctx):
    """KI wünscht allen eine gute Nacht"""
    await ctx.send('Ich wünsche allen eine GuNa!')


@bot.command()
async def bye(ctx):
    """KI verabschiedet sich"""
    bye = ["Bis denne Antenne!", "Ching Chang Ciao!", "Tschüsseldorf!", "Tschüßi Müsli!", "Tschüßli Müsli!",
           "Bis Spätersilie!", "San Frantschüssko!", "Bis Baldrian!", "Bye mit Ei!", "Tschau mit au!", "Tschö mit ö!",
           "Hau Rheinwald!", "Schalömmchen!", "Schönes Knochenende!", "Tschüssikowski!", "Tüdelü in aller Früh!"]

    await ctx.send(bye[random.randint(0, 15)])


@bot.command()
async def sev(ctx):
    """Sev ist behindert"""
    await ctx.send('https://de.wikihow.com/Einen-ganzen-Tag-lang-schweigen')


@bot.command()
async def lukas(ctx):
    """Lukas ist behindert"""
    await ctx.send('https://de.wikihow.com/Mit-einer-geistig-behinderten-person-kommunizieren')


@bot.command(aliases=["johannes", "jojo"])
async def nils(ctx):
    """Nils und Johannes sind behindert"""
    await ctx.send('https://de.wikihow.com/Mit-gemeinen-Menschen-richtig-umgehen')


# !react bruh
@bot.command()
async def react(ctx, reaction):
    """KI reagiert auf die zuletzt geschriebene Nachricht mit {reaction}"""

    reaction_list = list(reaction)
    # TODO do this
    for letter in reaction_list:
        await ctx.message.add_reaction()


bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
