import asyncio
import discord
from main import tokens
from discord.ext import commands


client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print(f'{client.user} ist online')
    await client.change_presence(activity=discord.Game('Upcoming: GAD Vl 13:15'), status=discord.Status.online)


@client.event
async def on_command_error(ctx, error, force=False):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('Command not found. :(')
    else:
        await ctx.send("I don't understand ._.")


@client.command()
async def clear(ctx, amount=1):
    """Delete the given amount of messages (default == 1) with !clear {amount}*"""
    await ctx.channel.purge(limit=amount+1)


@client.command()
async def event(ctx, *, event):
    """Change the current event with !event {event}"""
    await ctx.send(f'Current event changed to {event}')
    await client.change_presence(activity=discord.Game(f'Upcoming: {event}'), status=discord.Status.online)


@client.command()
async def chrissi(ctx):
    """Chrissi ist gemein und wird deshalb gemobbt"""
    await ctx.send('Chrissi ist ein dummer Hacker!', delete_after=7000)

@client.command()
async def gumo(ctx):
    """KI wünscht allen einen guten Morgen"""
    await ctx.send('Ich wünsche allen einen GuMo!')


@client.command()
async def guna(ctx):
    """KI wünscht allen eine gute Nacht"""
    await ctx.send('Ich wünsche allen eine GuNa!')


#!react bruh


#@commands.is_owner()
#Bot auf Server


client.run(tokens.token)
