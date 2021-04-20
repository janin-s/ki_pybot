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
async def on_command_error(ctx, error, force=False):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('KI dummdumm <:eist_moment:731293248324370483>')
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send("nicht so schnell")
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
            newcount = current-1
            await add_entry("data.json", "all", newcount)
        else:
            # newcount = await persistent_counter()
            current = int(get_entry("data.json", "all")[1])
            newcount = current+1
            await add_entry("data.json", "all", current+1)
        await ctx.send(f'Shot-Counter: {newcount}')
    else:
        await ctx.send('Jonas haut dich <:knast:731290033046159460>')

        
@bot.command()
async def catanverbot(ctx):
    """Catan spielen nur dofis"""
    await ctx.send('Bembl komm CS spielen!')

@bot.command(aliases=["hacker"])
async def chrissi(ctx):
    """Chrissi ist gemein und wird deshalb gemobbt"""
    await ctx.send('Chrissi ist so ein Lieber!')


@bot.command()
async def gumo(ctx):
    """KI wünscht allen einen guten Morgen"""
    user_name = ctx.message.author.display_name
    await ctx.send(user_name + ' wünscht allen einen GuMo!')


@bot.command()
async def gumi(ctx):
    """KI wünscht allen einen guten Mittag"""
    user_name = ctx.message.author.display_name
    await ctx.send(user_name + ' wünscht allen einen Guten Mittach!')

@bot.command()
async def guab(ctx):
    """KI wünscht allen einen guten Abend"""
    user_name = ctx.message.author.display_name
    await ctx.send(user_name + ' wünscht allen einen Guten Abend!')
    
@bot.command()
async def guna(ctx):
    """KI wünscht allen eine gute Nacht"""
    user_name = ctx.message.author.display_name
    await ctx.send(user_name + ' wünscht allen eine GuNa!')

@bot.command()
async def gugebu(ctx):
    persons = ctx.message.mentions
    for person in persons:
        await ctx.send("Alles Gute " + person.display_name + "!")

@bot.command()
async def bye(ctx):
    """KI verabschiedet sich"""
    bye = ["Bis denne Antenne!", "Ching Chang Ciao!", "Tschüsseldorf!", "Tschüßli Müsli!",
           "Bis Spätersilie!", "San Frantschüssko!", "Bis Baldrian!", "Bye mit Ei!", "Tschau mit au!", "Tschö mit ö!",
           "Hau Rheinwald!", "Schalömmchen!", "Schönes Knochenende!", "Tschüssikowski!", "Tüdelü in aller Früh!"]

    await ctx.send(bye[random.randint(0, len(bye)-1)])


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
async def jan(ctx):
    await ctx.send('Jan ist sehr nett und lieb!')


@bot.command()
async def lukas(ctx):
    """Lukas ist nicht nett"""
    await ctx.send('https://de.wikihow.com/Mit-einer-geistig-behinderten-person-kommunizieren')


@bot.command(aliases=["johannes", "jojo"])
async def nils(ctx):
    """Nils und Johannes sind nicht nett"""
    await ctx.send('https://www.muenchen-heilpraktiker-psychotherapie.de/blog-2/selbstbewusstsein/10-anzeichen-dass-sie-zu-nett-sind-fuer-diese-welt.html')


@bot.command()
async def piep(ctx):
    """nur liebe auf diesem server"""
    await ctx.send("piep piep, wir ham uns alle lieb! <:liebruh:731289435886583951>")

@bot.command()
async def amen(ctx):
    """beten macht spaß"""
    await ctx.send("Vater unser da oben, wir wollen dich loben\nhier steht ganz viel dreck, mach die sünden weg\namen")


@bot.command()
async def punish(ctx):
    """bestraft alle mentioned user mit hass"""
    members = ctx.message.mentions
    for user in members:
        current_id = user.id
        if current_id != 453256761906954255 and user.status is discord.Status.offline:
            await ctx.send("offline User punishen sehr gemein, lass das :(")
            continue
        elif current_id == 709865255479672863:
            user = ctx.message.author
            current_id = user.id
            await ctx.send("KI schlägt zurück")
        else:
            last_punish_string = get_entry("punish_times.json", current_id)[1]
            try:
                last_punish: datetime = datetime.fromisoformat(last_punish_string)
            except ValueError:
                last_punish: datetime = datetime.min
            if (datetime.now() - last_punish) < timedelta_12_h:
                await ctx.send(user.display_name + " wurde vor kurzem erst bestraft!")
                continue

        await kick_with_invite_and_roles(ctx, user, current_id)
        await add_entry("punish_times.json", str(current_id), datetime.now().isoformat())


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
            r1 = await add_entry("raubkopien.json", str(t.date().isoformat()), str(param2)) if command == "add" else await remove_entry("raubkopien.json", str(t.date().isoformat()))
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


async def kick_with_invite_and_roles(ctx, user, user_id):
    current_roles = map(lambda x: x.id, user.roles)
    nick = user.display_name
    user_roles[user_id] = current_roles
    user_nicks[user_id] = nick

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


@bot.command()
async def add_user_wichtellist(ctx):
    if ctx.message.author.id != 139418002369019905:
        await ctx.send("nur der Wichtel Meister darf das")
    else:
        wichtler = ctx.message.mentions
        ids = [user.id for user in wichtler]
        with open("data/wichtel_list.json", "r") as fr:
            inhalt: list = json.load(fr)
        for id in ids:
            if id not in inhalt:
                inhalt.append(id)

                with open("data/has_wichtel_partner.json", "r") as pr:
                    has_partner = json.load(pr)
                has_partner[id] = False
                with open("data/has_wichtel_partner.json", "w") as pw:
                    json.dump(has_partner, pw, separators=(',', ': '), indent=4)

        with open("data/wichtel_list.json", "w") as fw:
            json.dump(inhalt, fw, separators=(',', ':'), indent=4)

        await ctx.send(f"added ids: {ids}")


@bot.command()
async def wichtel(ctx):
    if ctx.message.author.id != 139418002369019905:
        await ctx.send("nur der Wichtel Meister darf das")
        return

    with open("data/wichtel_list.json", "r") as fr:
        inhalt: list = json.load(fr)
    count_users = len(inhalt)
    for i in range(count_users):
        await wichtel_pair(ctx, inhalt[i])


async def wichtel_pair(ctx, user_id):
    user = await bot.fetch_user(user_id)
    with open("data/has_wichtel_partner.json", "r") as pr:
        has_partner = json.load(pr)
    try:
        has_partner_current = has_partner[user.id]
    except KeyError:
        has_partner_current = False

    if not has_partner_current:
        with open("data/wichtel_list.json", "r") as fr:
            wichtler: list = json.load(fr)
        index = random.randrange(len(wichtler))
        while wichtler[index] == user.id:
            if len(wichtler) == 1:
                await ctx.send("wichtelprozess ist gefickt")
                return
            index = random.randrange(len(wichtler))
        partner_id = wichtler.pop(index)
        partner = await bot.fetch_user(partner_id)
        dm_channel = user.dm_channel
        await ctx.send(user.display_name + " hat einen Wichtelpartner erhalten")
        try:
            if dm_channel is None:
                dm_channel = await user.create_dm()
            await dm_channel.send("Dein Wichtelpartner ist: " + partner.display_name)

            with open("data/has_wichtel_partner.json", "r") as pr:
                has_partner = json.load(pr)
            has_partner[user.id] = True
            with open("data/has_wichtel_partner.json", "w") as pw:
                json.dump(has_partner, pw, separators=(',', ': '), indent=4)

        except discord.Forbidden:
            wichtler.append(partner_id)
            await ctx.send("nvm, du ehrenloser hast PMs aus :(")

        with open("data/wichtel_list.json", "w") as fw:
            json.dump(wichtler, fw, separators=(',', ':'), indent=4)
    else:
        await ctx.send("Du hast bereits einen Partner!")
bot.run('NzA5ODY1MjU1NDc5NjcyODYz.XrsH2Q.46qaDs7GDohafDcEe5Ruf5Y7oGY')
