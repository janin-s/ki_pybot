import random

from helper_functions import *
from datetime import datetime, timedelta
from typing import Union

import dateutil
from dateutil import parser

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
user_roles: dict = dict()
user_nicks: dict = dict()
timedelta_12_h = timedelta(hours=12)


@bot.event
async def on_ready():
    print(f'{bot.user} ist online')
    await bot.change_presence(activity=discord.Game('Semesterstart kickt'), status=discord.Status.online)


@bot.event
async def on_command_error(ctx, error, force=False):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('KI dummdumm <:eist_moment:731293248324370483>')
    elif isinstance(error, commands.errors.CommandOnCooldown):
        pass
    elif isinstance(error, commands.errors.BotMissingPermissions):
        await ctx.send("KI nicht mächtig genug :(")
    else:
        await ctx.send("KI nix verstehi ._." + str(error))


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


@bot.command()
async def clear(ctx, amount=1):
    """Löscht die übergebene Anzahl an Messages (default == 1) mit !clear {amount}*"""
    if ctx.channel.id == 705427122151227442:
        await ctx.message.delete
        await ctx.send('Pseudohistorie wird hier nicht geduldet!', delete_after=60)
    else:
        wichtig = ctx.message.guild.get_role(705430318131314798)
        if wichtig not in ctx.author.roles:
            purge_limit = min(amount + 1, 10)
        else:
            # zur sicherheit
            purge_limit = min(amount + 1, 200)
        await ctx.channel.purge(limit=purge_limit)


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
async def hausaufgabenhilfe(ctx):
    """individuelle hausaufgabenhilfe für jeden"""
    if ctx.message.author.id == 388061626131283968:
        await ctx.send('https://blog.onlyfans.com/5-steps-for-getting-started-on-onlyfans/')
    elif ctx.message.author.id == 174900012340215809:
        await ctx.send("lüg nicht, eh schon alles 100%")
    else:
        await ctx.send('Du schaffst das schon! KI glaubt an dich :)')


@bot.command()
async def janin(ctx):
    """janin ist gemein"""
    await ctx.send('https://www.wikihow.com/Drop-Out-of-College')


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
async def react(ctx, reaction, message_id: Union[int, str] = 0):
    """!react {reaction} [message-id]; nur für Isogramme, Zahlen und !?"""
    if type(message_id) is not int or not await are_characters_unique(reaction):
        await ctx.send("Uncooles Wort, KI will nicht <:sad2:731291939571499009>")
        return
    if message_id != 0:
        try:
            message = await ctx.fetch_message(message_id)
            await ctx.message.delete()
        except discord.NotFound:
            await ctx.send("Message (" + str(message_id) + ") weg, oh no :(")
            return
    else:
        try:
            message = await ctx.channel.history(limit=1, before=ctx.channel.last_message).get()
            await ctx.message.delete()
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


@bot.command()
async def punish(ctx):
    """bestraft alle mentioned user mit hass"""
    user_list = ctx.message.mentions
    for user in user_list:
        current_id = user.id
        if (current_id != 453256761906954255) and (user.status is discord.Status.offline):
            await ctx.send("offline User punishen sehr gemein, lass das :(")
            continue
        if current_id == 709865255479672863:
            user = ctx.message.author
            current_id = user.id
            await ctx.send("KI schlägt zurück")
        else:
            last_punish: datetime = await get_punish_time(current_id)
            if (datetime.now() - last_punish) < timedelta_12_h:
                await ctx.send(user.display_name + " wurde vor kurzem erst bestraft!")
                continue

        current_roles = map(lambda x: x.id, user.roles)
        nick = user.display_name
        user_roles[current_id] = current_roles
        user_nicks[current_id] = nick

        dm_channel = user.dm_channel
        await ctx.send(nick + " soll sich schämen gehen")
        invite = await ctx.channel.create_invite(max_uses=1)
        try:
            if dm_channel is None:
                dm_channel = await user.create_dm()
            for i in range(4):
                await dm_channel.send("shame!")
            await dm_channel.send("https://media.giphy.com/media/vX9WcCiWwUF7G/giphy.gif")
            await dm_channel.send(invite.url)
        except discord.Forbidden:
            pass
        try:
            await user.kick(reason="Bestrafung")
        except discord.Forbidden:
            await ctx.send("KI nicht mächtig genug")
        await set_punish_time(current_id, datetime.now())


@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def hug(ctx):
    """umarmt alle mentioned user privat. 1 min cooldown"""
    user_list = ctx.message.mentions

    for user in user_list:
        current_id = user.id
        if current_id == 709865255479672863:
            user = ctx.message.author
            name = "KI"
            await ctx.send("KI hat dich auch lieb!")
        else:
            name = ctx.message.author.display_name
        await ctx.send(ctx.message.author.display_name + " versendet eine Umarmung an " + user.display_name + "!")

        dm_channel = user.dm_channel
        try:
            if dm_channel is None:
                dm_channel = await user.create_dm()
            await dm_channel.send("Liebe! " + name + " sendet dir eine Umarmung!")
            await dm_channel.send("https://i.pinimg.com/originals/e2/f7/2a/e2f72a771865ea0d74895cb2c2199a83.gif")
        except discord.Forbidden:
            pass
    await ctx.message.delete()


@bot.command()
async def raubkopie(ctx, command="", param: str = "", param2: Union[str, id] = 0):
    """!raubkopie add ["today"/XX.XX.XX] [link]
        !raubkopie remove ["today"/XX.XX.XX]
        !raubkopie get ["list"/"id"/XX.XX.XX] [id]"""
    r = "nicht gefunden, kp warum :("
    if command == "add" or command == "remove":
        if ctx.message.author.id == 174900012340215809 or ctx.message.author.id == 139418002369019905:
            if param == "today":
                t: datetime = datetime.now()
            else:
                info = dateutil.parser.parserinfo(dayfirst=True)
                t: datetime = dateutil.parser.parse(str(param), parserinfo=info)
            print("parsed time: " + t.isoformat())
            r = add_raubkopie(t, str(param2)) if command == "add" else remove_raubkopie(t)
        else:
            await ctx.send("nur chrissi darf das!")
            return
    elif command == "get":
        if param == "id":
            try:
                r = await get_raubkopie(int(param2))
            except ValueError:
                await ctx.send("id komisch :(")
                return
        elif param == "list":
            r = await get_raubkopie_all()
        else:
            try:
                info = dateutil.parser.parserinfo(dayfirst=True)
                t: datetime = dateutil.parser.parse(str(param), parserinfo=info)
                print("parsed time: " + t.isoformat())
                r = await get_raubkopie(t)
            except ValueError:
                await ctx.send("datum komisch, nix verstehi :(")
                return
    await ctx.send(r)


bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
