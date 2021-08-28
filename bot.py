import random
import sys

from helper_functions import *
from datetime import datetime, timedelta
from typing import Union
import threading

import dateutil
from dateutil import parser

import discord
import json
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
user_roles: dict = dict()
user_nicks: dict = dict()
timedelta_12_h = timedelta(hours=12)
VOTEKICK_NO = 4


@bot.event
async def on_ready():
    if not os.path.isdir(r"data_files"):
        os.makedirs("./data_files")
    if not os.path.isfile(r"data/data.json"):
        with open(r"data/data.json", "w") as data:
            json.dump({}, data, separators=(',', ': '), indent=4)
    if not os.path.isfile(r"data/punish_times.json"):
        with open(r"data/punish_times.json", "w") as punish_times:
            json.dump({}, punish_times, separators=(',', ': '), indent=4)
    if not os.path.isfile(r"data/raubkopien.json"):
        with open(r"data/raubkopien.json", "w") as raubkopien:
            json.dump({}, raubkopien, separators=(',', ': '), indent=4)
    if not os.path.isfile(r"data/votekick.json"):
        with open(r"data/votekick.json", "w") as votekick:
            json.dump({}, votekick, separators=(',', ': '), indent=4)
    if not os.path.isfile(r"data/wichtel_list.json"):
        with open(r"data/wichtel_list.json", "w") as wichtel:
            json.dump([], wichtel, separators=(',', ': '), indent=4)
    if not os.path.isfile(r"data/has_wichtel_partner.json"):
        with open(r"data/has_wichtel_partner.json", "w") as partner:
            json.dump({}, partner, separators=(',', ': '), indent=4)
    print(f'{bot.user} ist online')
    await bot.change_presence(activity=discord.Game('Semesterstart kickt'), status=discord.Status.online)


@bot.event
async def on_member_join(member):
    if member.id in user_roles:
        for role_id in user_roles[member.id]:
            role = discord.utils.get(member.guild.roles, id=role_id)
            if role.name == "@everyone":
                pass
            else:
                await member.add_roles(role)

    if member.id in user_nicks:
        await member.edit(nick=user_nicks[member.id])


@bot.command(aliases=["rip", "suizid", "lost"])
async def shot(ctx, *, command=None):
    """Erhöht den Shot-Counter um 1"""
    if ctx.message.author.id == 388061626131283968 or ctx.message.author.id == 295927454562779139:
        if command == "reset":
            # newcount = await persistent_counter(caller="resetAll")
            await add_entry("data.json", "all", 0)
            newcount = 0
        elif command == "drink":
            # newcount = await persistent_counter(increment=False)
            current = int(get_entry("data.json", "all")[1])
            if current <= 0:
                await ctx.send("alle shots leergetrunken")
            newcount = current - 1
            await add_entry("data.json", "all", newcount)
        else:
            # newcount = await persistent_counter()
            current = int(get_entry("data.json", "all")[1])
            newcount = current + 1
            await add_entry("data.json", "all", current + 1)
        await ctx.send(f'Shot-Counter: {newcount}')
    else:
        await ctx.send('Jonas haut dich <:knast:731290033046159460>')


@bot.command()
async def hausaufgabenhilfe(ctx):
    """individuelle hausaufgabenhilfe für jeden"""
    if ctx.message.author.id == 388061626131283968:
        await ctx.send('https://blog.onlyfans.com/5-steps-for-getting-started-on-onlyfans/')
    elif ctx.message.author.id == 174900012340215809:
        await ctx.send("lüg nicht, eh schon alles 100%")
    else:
        await ctx.send('Du schaffst das schon! KI glaubt an dich :)')



@bot.command(aliases=["raubkopien"])
async def raubkopie(ctx, command="", param: str = "", param2: Union[str, id] = 0):
    """!raubkopie get ["list"/"id"/XX.XX.XX] [id]; !raubkopie add ["today"/XX.XX.XX] [link]"""

    r1 = "r1 not found :("
    if command == "add" or command == "remove":
        if ctx.message.author.id == 174900012340215809 or ctx.message.author.id == 139418002369019905:
            if param == "today":
                t: datetime = datetime.now()
            else:
                info = dateutil.parser.parserinfo(dayfirst=True)
                t: datetime = dateutil.parser.parse(str(param), parserinfo=info)
            print("parsed time: " + t.isoformat())
            # r = add_raubkopie(t, str(param2)) if command == "add" else remove_raubkopie(t)
            r1 = await add_entry("raubkopien.json", str(t.date().isoformat()),
                                 str(param2)) if command == "add" else await remove_entry("raubkopien.json",
                                                                                          str(t.date().isoformat()))
        else:
            await ctx.send("nur chrissi darf das!")
            return
    elif command == "reset":
        if ctx.message.author.id == 174900012340215809 or ctx.message.author.id == 139418002369019905:
            path = os.path.join("data_files", param)
            if os.path.isfile(path):
                reset_file(path)
                await ctx.send("cleared file")
            else:
                await ctx.send("file existiert nicht")
            return
        else:
            await ctx.send("nur chrissi darf das!")
            return
    elif command == "get":
        if param == "id":
            try:
                await ctx.send("Dieses Feature folgt bald, vielen Dank für Ihre Geduld!")
                return
                # TODO entries nach datum sortieren und id nutzen
                # r1 = get_entry("test", param2)
            except ValueError:
                await ctx.send("id komisch lokal :(")
                return
        elif param == "list":
            # r = await get_raubkopie_all()
            r1_dict = get_file("raubkopien.json")
            r1 = str(r1_dict)
            # listembed = discord.Embed(title="Aufzeichnungsliste", description=r)
            listembed2 = discord.Embed(title="Aufzeichnungsliste", description=str(r1))
            # await ctx.send(embed=listembed)
            await ctx.send(embed=listembed2)
            return
        else:
            try:
                info = dateutil.parser.parserinfo(dayfirst=True)
                t: datetime = dateutil.parser.parse(str(param), parserinfo=info)
                print("parsed time: " + t.isoformat())
                # r = await get_raubkopie(t)
                r1 = get_entry("raubkopien.json", t.date().isoformat())
            except ValueError as e:
                await ctx.send("datum komisch, nix verstehi :( " + str(e))
                return
    await ctx.send(f"r1: {r1}")


@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def votekick(ctx):
    users = ctx.message.mentions
    amount: int = 1
    user = None
    if len(users) >= 1:
        user = users[0]
    else:
        return
    current_id = user.id
    name = ctx.message.author.display_name
    if current_id == 709865255479672863:
        name = "Jesus"
        user = ctx.message.author
        current_id = user.id
        await ctx.send("KI wird nicht gekickt!")
        amount = sys.maxsize

    current_votes = get_entry("votekick.json", current_id)[1]
    try:
        new_votes = int(current_votes) + amount
    except ValueError:
        new_votes = amount
    await ctx.send(f"{name} will {user.display_name} endlich weg haben ({new_votes}/{VOTEKICK_NO} voted)")
    if new_votes >= VOTEKICK_NO:
        await ctx.send("Das ist genug Hass für nen Kick. Winke Winke")
        await add_entry("votekick.json", str(current_id), 0)
        await kick_with_invite_and_roles(ctx, user, current_id)
    else:
        if new_votes == 1:
            timer = threading.Timer(119.0, reset_vote, args=[ctx, current_id])
            timer.start()
            print("started timer for id: " + str(current_id))
        await ctx.send("Das ist nicht genug Hass für nen Kick")
        await add_entry("votekick.json", str(current_id), str(new_votes))


# weil chrisl bot putt macht hat
def reset_vote(ctx, current_id):
    add_entry_unsync("votekick.json", str(current_id), 0)


@bot.command()
async def reset_vote_cmd(ctx, current_id):
    await ctx.send("reset")
    await add_entry("votekick.json", str(current_id), 0)


bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
