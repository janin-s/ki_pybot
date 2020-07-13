import discord
from discord.ext import commands


bot = commands.Bot(command_prefix='!')
bot_activity = ""
shot_counter = 0


@bot.event
async def on_ready():
    print(f'{bot.user} ist online')
    await bot.change_presence(activity=discord.Game('Next: Lerni für Klausuren'), status=discord.Status.online)


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
        await ctx.channel.purge(limit=amount+1)


@bot.command()
async def event(ctx, *, event):
    """Setze ein neues Event mit !event {event}"""
    await ctx.send(f'Current event changed to {event}')
    # global bot_activity
    # bot_activity = event
    await bot.change_presence(activity=discord.Game(f'Next: {event}'), status=discord.Status.online)

@bot.command(aliases=["shot", "shot_counter", "shout counter"])
async def rip(ctx):
        """Erhöht den Shot-Counter um 1"""
        global shot_counter
        shot_counter += 1
        await ctx.send(f'Shot-Counter: {shot_counter}')

@bot.command(aliases=["hacker"])
async def chrissi(ctx):
    """Chrissi ist gemein und wird deshalb gemobbt"""
    await ctx.send('Chrissi ist ein dummer Hacker!', delete_after=7000)


@bot.command()
async def gumo(ctx):
    """KI wünscht allen einen guten Morgen"""
    await ctx.send('Ich wünsche allen einen GuMo!')


@bot.command()
async def guna(ctx):
    """KI wünscht allen eine gute Nacht"""
    await ctx.send('Ich wünsche allen eine GuNa!')


@bot.command()
async def hallo(ctx):
    """KI wünscht allen eine gute Nacht"""
    await ctx.send('Hallo, I bims!')


#!react bruh
@bot.command()
async def react(ctx, reaction):
    """KI reagiert auf die zuletzt geschriebene Nachricht mit {reaction}"""
    await ctx.send('Chrissi behindert!')


#@commands.is_owner()
#Bot auf Server


bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
