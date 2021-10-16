import asyncio

from discord import User, Embed
from discord.ext.commands import *
from apscheduler.triggers.cron import CronTrigger

from ..utils import send_paginated, parse_datetime
from lib.db import db
from dateutil import parser
from datetime import datetime, timedelta
from operator import itemgetter


class Birthdays(Cog):
    def __init__(self, bot):
        bot.scheduler.add_job(self.congratulate, CronTrigger(hour=0))
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("birthdays")

    @group(aliases=['birthday', 'bd', 'bday'], invoke_without_command=True)
    async def birthdays(self, ctx):
        """"Birthdays"""
        embed = Embed(title="Birthdays")
        embed.add_field(name="aliases", value="You can use !birthday, !birthdays or !bd")
        embed.add_field(name="add", value="Use !bd add <date> to add your birthday")
        embed.add_field(name="list", value="Use !bd list [<date>] to get a list of some or all birthdays")
        embed.add_field(name="date",
                        value="Use MM.DD[.YYYY] or 'today/heute' and 'tomorrow/morgen'")
        embed.set_thumbnail(
            url="https://sallysbakingaddiction.com/wp-content/uploads/2017/05/ultimate-birthday-cupcakes.jpg")
        await ctx.send(embed=embed)

    @birthdays.command()
    async def add(self, ctx, *, birthdate):
        try:
            date = parse_datetime(birthdate)
        except ValueError:
            await ctx.message.add_reaction('\U0000274C')
            return
        print(f"adding bd of {ctx.message.author.display_name} on day {date.day} and month {date.month}")
        db.execute("REPLACE INTO birthdays (guild_id, user_id, month, day) VALUES (?,?,?,?)",
                   ctx.guild.id, ctx.message.author.id, date.month, date.day)
        await ctx.message.add_reaction('\U00002705')

    @birthdays.command()
    async def list(self, ctx, *, birthdate=""):
        if birthdate == "":
            result = db.records("SELECT user_id, month, day FROM birthdays WHERE guild_id = ?", ctx.guild.id)
        else:
            try:
                date = parse_datetime(birthdate)
            except ValueError:
                date = datetime.now()
            result = db.records(
                "SELECT user_id, month, day FROM birthdays WHERE guild_id = ? AND day = ? AND month = ?",
                ctx.guild.id, date.day, date.month)
        if result is None or len(result) is 0:
            await ctx.send('no birthdays found')
            return
        bds = [f"{ctx.guild.get_member(id).display_name}: {d:02d}.{m:02d}" for (id, m, d) in
               sorted(result, key=itemgetter(1, 2))]
        msg = "\n".join(bds)
        await send_paginated(ctx, start="```", end="```", content=msg)

    async def congratulate(self):
        await asyncio.sleep(1)  # idk how precise CronTrigger is, make sure we have the next day
        day = datetime.today().day
        month = datetime.today().month
        for guild in self.bot.guilds:
            print("fetching channels")
            channel_id = db.field("SELECT birthday_channel FROM server_info WHERE guild_id = ?", guild.id)
            if channel_id is None:
                channel_id = db.field("SELECT main_channel FROM server_info WHERE guild_id = ?", guild.id)
            if channel_id is None:
                print(f"didnt find channel for guild {guild.id}")
                continue
            channel = await self.bot.fetch_channel(channel_id)
            ids = db.column("SELECT user_id FROM birthdays WHERE month = ? AND day = ? AND guild_id = ?",
                            month, day, guild.id)
            print(f"found {len(ids)} users for day {day} and month {month}")
            for id in ids:
                user: User = await self.bot.fetch_user(id)
                if user is not None:
                    print(f"User with display name{user.display_name} and name {user.name}")
                    await channel.send(f"Alles Gute {user.mention}!")


def setup(bot):
    bot.add_cog(Birthdays(bot))
