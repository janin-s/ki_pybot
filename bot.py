import fileinput
import random
from typing import Any, Coroutine, Iterator

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', case_insensitive=True)
shot_counter = 0

letter_dict = {'A': 'regional_indicator_a', 'B': 'regional_indicator_b', 'C': 'regional_indicator_c',
               'D': 'regional_indicator_d', 'E': 'regional_indicator_e', 'F': 'regional_indicator_f',
               'G': 'regional_indicator_g', 'H': 'regional_indicator_h', 'I': 'regional_indicator_i',
               'J': 'regional_indicator_j', 'K': 'regional_indicator_k', 'L': 'regional_indicator_l',
               'M': 'regional_indicator_m', 'N': 'regional_indicator_n', 'O': 'regional_indicator_o',
               'P': 'regional_indicator_p', 'Q': 'regional_indicator_q', 'R': 'regional_indicator_r',
               'S': 'regional_indicator_s', 'T': 'regional_indicator_t', 'U': 'regional_indicator_u',
               'V': 'regional_indicator_v', 'W': 'regional_indicator_w', 'X': 'regional_indicator_x',
               'Y': 'regional_indicator_y', 'Z': 'regional_indicator_z', 'a': 'regional_indicator_a',
               'b': 'regional_indicator_b', 'c': 'regional_indicator_c', 'd': 'regional_indicator_d',
               'e': 'regional_indicator_e', 'f': 'regional_indicator_f', 'g': 'regional_indicator_g',
               'h': 'regional_indicator_h', 'i': 'regional_indicator_i', 'j': 'regional_indicator_j',
               'k': 'regional_indicator_k', 'l': 'regional_indicator_l', 'm': 'regional_indicator_m',
               'n': 'regional_indicator_n', 'o': 'regional_indicator_o', 'p': 'regional_indicator_p',
               'q': 'regional_indicator_q', 'r': 'regional_indicator_r', 's': 'regional_indicator_s',
               't': 'regional_indicator_t', 'u': 'regional_indicator_u', 'v': 'regional_indicator_v',
               'w': 'regional_indicator_w', 'x': 'regional_indicator_x', 'y': 'regional_indicator_y',
               'z': 'regional_indicator_z'}


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
        await ctx.send('Jonas haut dich <:knast:731290033046159460>')


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
            return 0
        return number


@bot.command(aliases=["hacker"])
async def chrissi(ctx):
    """Chrissi ist gemein und wird deshalb gemobbt"""
    await ctx.send('Chrissi macht Bot kaputt und ist ein dummer Hacker!!')


@bot.command(aliases=["frech"])
async def janin(ctx):
    for c in "faul":
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
    if not await areCharactersUnique(reaction):
        await ctx.send("uncooles wort, KI will nicht")
        return

    letter_list = list(reaction)
    # id_list = map(getUnicodeId, letter_list)
    for letter in letter_list:
        unicode_id: str = await getUnicodeId(letter)
        unicode_id: str = unicode_id.upper()

        await ctx.send(unicode_id)
        await ctx.message.add_reaction("\U0001F1F7")
        await ctx.message.add_reaction(unicode_id)


async def getUnicodeId(c):
    id_dec: int = 127462 + ((ord(c) - 65) if c.isupper() else (ord(c) - 97))
    id_hex: str = hex(id_dec)[2:]
    return "\\U000" + id_hex


async def areCharactersUnique(s):
    # hilfsfunktion dreist von g4g geklaut
    # https://www.geeksforgeeks.org/efficiently-check-string-duplicates-without-using-additional-data-structure/
    # An integer to store presence/absence
    # of 26 characters using its 32 bits
    checker = 0

    for i in range(len(s)):

        val = ord(s[i]) - ord('a')

        # If bit corresponding to current
        # character is already set
        if (checker & (1 << val)) > 0:
            return False

        # set bit in checker
        checker |= (1 << val)

    return True


bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
