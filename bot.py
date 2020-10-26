import fileinput
import random
from typing import Any, Coroutine, Iterator

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', case_insensitive=True)
shot_counter = 0

letter_dict = {'A': '\U0001f1e6', 'B': '\U0001f1e7', 'C': '\U0001f1e8', 'D': '\U0001f1e9', 'E': '\U0001f1ea',
               'F': '\U0001f1eb', 'G': '\U0001f1ec', 'H': '\U0001f1ed', 'I': '\U0001f1ee', 'J': '\U0001f1ef',
               'K': '\U0001f1f0', 'L': '\U0001f1f1', 'M': '\U0001f1f2', 'N': '\U0001f1f3', 'O': '\U0001f1f4',
               'P': '\U0001f1f5', 'Q': '\U0001f1f6', 'R': '\U0001f1f7', 'S': '\U0001f1f8', 'T': '\U0001f1f9',
               'U': '\U0001f1fa', 'V': '\U0001f1fb', 'W': '\U0001f1fc', 'X': '\U0001f1fd', 'Y': '\U0001f1fe',
               'Z': '\U0001f1ff', 'a': '\U0001f1e6', 'b': '\U0001f1e7', 'c': '\U0001f1e8', 'd': '\U0001f1e9',
               'e': '\U0001f1ea', 'f': '\U0001f1eb', 'g': '\U0001f1ec', 'h': '\U0001f1ed', 'i': '\U0001f1ee',
               'j': '\U0001f1ef', 'k': '\U0001f1f0', 'l': '\U0001f1f1', 'm': '\U0001f1f2', 'n': '\U0001f1f3',
               'o': '\U0001f1f4', 'p': '\U0001f1f5', 'q': '\U0001f1f6', 'r': '\U0001f1f7', 's': '\U0001f1f8',
               't': '\U0001f1f9', 'u': '\U0001f1fa', 'v': '\U0001f1fb', 'w': '\U0001f1fc', 'x': '\U0001f1fd',
               'y': '\U0001f1fe', 'z': '\U0001f1ff', '0': '\U00000030\U000020E3', '1': '\U00000031\U000020E3',
               '2': '\U00000032\U000020E3', '3': '\U00000033\U000020E3', '4': '\U00000034\U000020E3',
               '5': '\U00000035\U000020E3', '6': '\U00000036\U000020E3', '7': '\U00000037\U000020E3',
               '8': '\U00000038\U000020E3', '9': '\U00000039\U000020E3', '?': '\U00002753', '!': '\U00002757'}


@bot.event
async def on_ready():
    print(f'{bot.user} ist online')
    await bot.change_presence(activity=discord.Game('Semesterstart kickt'), status=discord.Status.online)


@bot.event
async def on_command_error(ctx, error, force=False):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('KI dummdumm <:eist_moment:731293248324370483>')
    else:
        await ctx.send("KI nix verstehi ._." + str(error))


@bot.command()
async def clear(ctx, amount=1):
    """Löscht die übergebene Anzahl an Messages (default == 1) mit !clear {amount}*"""
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


@bot.command()
async def gumo(ctx):
    """KI wünscht allen einen guten Morgen"""
    user_name = ctx.message.author.display_name
    await ctx.send(user_name + ' wünscht allen einen GuMo!')


@bot.command()
async def gumi(ctx):
    """KI wünscht allen einen guten Mittag"""
    user_name = ctx.message.author.display_name
    await ctx.send(user_name + ' wünscht allen einen GuMi!')


@bot.command()
async def guna(ctx):
    """KI wünscht allen eine gute Nacht"""
    user_name = ctx.message.author.display_name
    await ctx.send(user_name + ' wünscht allen eine GuNa!')


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
    await ctx.send('<:cursed:768963579973992468> https://de.wikihow.com/Einen-ganzen-Tag-lang-schweigen')


@bot.command()
async def lukas(ctx):
    """Lukas ist behindert"""
    await ctx.send('https://de.wikihow.com/Mit-einer-geistig-behinderten-person-kommunizieren')


@bot.command(aliases=["johannes", "jojo"])
async def nils(ctx):
    """Nils und Johannes sind behindert"""
    await ctx.send('https://de.wikihow.com/Mit-gemeinen-Menschen-richtig-umgehen')


@bot.command()
async def zitat(ctx, length=1):
    """!zitat [x]; zitiert die letze[n x] Nachricht[en] und speichert sie in Relikte"""
    zitat: str = ""
    message_list = []
    async for message in ctx.channel.history(limit=length + 1):
        message_list.append(message)
    message_list.reverse()
    for i in range(0, len(message_list) - 1):
        zitat += message_list[i].author.display_name + ": \"" + message_list[i].content + "\"\n"
    relikte = await bot.fetch_channel(705427122151227442)
    await relikte.send(zitat)


@bot.command()
async def react(ctx, reaction, message_id=0):
    """!react {reaction} [message-id]; nur für Isogramme, Zahlen und !?"""
    if not await are_characters_unique(reaction):
        await ctx.send("Uncooles Wort, KI will nicht <:sad2:731291939571499009>")
        return
    if message_id != 0:
        try:
            message = await ctx.fetch_message(message_id)
            await ctx.channel.purge(limit=1)
        except discord.NotFound:
            await ctx.send("Message (" + str(message_id) + ") weg, oh no :(")
            return
    else:
        try:
            message = await ctx.channel.history(limit=1, before=ctx.channel.last_message).get()
            await ctx.channel.purge(limit=1)
        except discord.HTTPException:
            await ctx.send("message weg, oh no")
            return
    if (len(message.reactions) + len(reaction)) > 20:
        await ctx.send("Nils ist behindert", delete_after=10)
        return
    for letter in list(reaction):
        # unicode_id: str = letter_dict.get(letter)
        unicode_id = get_unicode_id(letter)
        await message.add_reaction(unicode_id)


async def are_characters_unique(s):
    # hilfsfunktion dreist von g4g geklaut und wild hässlich gemacht
    # https://www.geeksforgeeks.org/efficiently-check-string-duplicates-without-using-additional-data-structure/
    # An integer to store presence/absence
    # of 26 characters using its 32 bits
    checker = 0
    # 0 to 9, ?, !
    numbers_and_special = list(map(lambda x: False, range(0, 13)))
    s = s.lower()
    for i in range(len(s)):
        ascii_value = ord(s[i])
        if ascii_value < 97 or ascii_value > 122:
            if 48 <= ascii_value <= 57:
                if numbers_and_special[ascii_value - 48]:
                    return False
                else:
                    numbers_and_special[ascii_value - 48] = True
            else:
                if ascii_value == 63:
                    if numbers_and_special[10]:
                        return False
                    else:
                        numbers_and_special[10] = True
                else:
                    if ascii_value == 33:
                        if numbers_and_special[11]:
                            return False
                        else:
                            numbers_and_special[11] = True
                    else:
                        return False
        else:
            val = ascii_value - ord('a')

            # If bit corresponding to current
            # character is already set
            if (checker & (1 << val)) > 0:
                return False

            # set bit in checker
            checker |= (1 << val)

    return True


def get_unicode_id(c):
    c = c.lower()
    o = ord(c)
    if o < 97 or o > 122:
        return chr(127462 + (o - 97))
    if 48 <= o <= 57:
        return c + chr(8419)
    if c == 63:
        return '\U00002753'
    if c == 33:
        return '\U00002757'
    return 0


bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
