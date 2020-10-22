import random

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
bot_activity = ""
shot_counter = 0

bye = ["Bis denne Antenne!", "Ching Chang Ciao!", "Tschüsseldorf!", "Tschüßi Müsli!", "Tschüßli Müsli!",
       "Bis Spätersilie!", "San Frantschüssko!", "Bis Baldrian!", "Bye mit Ei!", "Tschau mit au!", "Tschö mit ö!",
       "Hau Rheinwald!", "Schalömmchen!", "Schönes Knochenende!", "Tschüssikowski!", "Tüdelü in aller Früh!"]

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
    # global bot_activity
    # bot_activity = event
    await bot.change_presence(activity=discord.Game(f'{event}'), status=discord.Status.online)


@bot.command(aliases=["rip", "suizid", "lost"])
async def shot(ctx):
    """Erhöht den Shot-Counter um 1"""
    if ctx.message.author.id == 388061626131283968 or ctx.message.author.id == 295927454562779139:
        global shot_counter
        shot_counter += 1
        await ctx.send(f'Shot-Counter: {shot_counter}')
    else:
        await ctx.send('Jonas haut dich <:knast:731290033046159460>', delete_after=60)


@bot.command(aliases=["hacker"])
async def chrissi(ctx):
    """Chrissi ist gemein und wird deshalb gemobbt"""
    await ctx.send('Chrissi ist ein gemeiner Lügner!', delete_after=7000)


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
    """KI wünscht allen einen guten Morgen"""
    await ctx.send(bye[random.randint(0, 15)])

@bot.command()
async def sev(ctx):
    """Sev ist behindert"""
    await ctx.send('https://de.wikihow.com/Einen-ganzen-Tag-lang-schweigen')

# !react bruh
@bot.command()
async def react(ctx, reaction):
    """KI reagiert auf die zuletzt geschriebene Nachricht mit {reaction}"""
    await ctx.send('Dieses Feature existiert noch nicht, weil Janin faul ist! >:( Kann doch nicht wahr sein, wir warten alle schon lange auf !react, schlimmer als Krusche!')


# @commands.is_owner()
# Bot auf Server


bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
