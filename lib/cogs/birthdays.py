import asyncio
from datetime import datetime
from operator import itemgetter

from discord import User, Embed
from discord.ext.commands import Cog, group, command
from apscheduler.triggers.cron import CronTrigger

from lib.db import db
from ..utils import send_paginated, parse_datetime



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
                        value="Use DD.MM[.YYYY] or 'today/heute' and 'tomorrow/morgen'")
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
        if result is None or len(result) == 0:
            await ctx.send('no birthdays found')
            return
        # sort so list starts at next bd and wraps
        bds_all1 = sorted(result, key=itemgetter(1, 2))
        bds_all2 = bds_all1
        today_day = datetime.today().day
        today_month = datetime.today().month
        bds_sorted1 = list(
            filter(lambda t: int(t[1]) > today_month or (int(t[1]) == today_month and int(t[2]) >= today_day),
                   bds_all1))
        bds_sorted2 = list(
            filter(lambda t: int(t[1]) < today_month or (int(t[1]) == today_month and int(t[2]) < today_day),
                   bds_all2))
        bds_all = bds_sorted1 + bds_sorted2

        msg = "\n".join([f"{ctx.guild.get_member(id).display_name}: {d:02d}.{m:02d}" for (id, m, d) in bds_all
                         if ctx.guild.get_member(id) is not None])
        await send_paginated(ctx, start="```", end="```", content=msg)

    async def congratulate(self):
        await asyncio.sleep(1)  # make sure we have the next day
        day = datetime.today().day
        month = datetime.today().month
        for guild in self.bot.guilds:
            channel_id = db.field("SELECT birthday_channel FROM server_info WHERE guild_id = ?", guild.id)
            if channel_id is None:
                channel_id = db.field("SELECT main_channel FROM server_info WHERE guild_id = ?", guild.id)
            if channel_id is None:
                print(f"didnt find channel for guild {guild.id}")
                continue
            channel = await self.bot.fetch_channel(channel_id)
            if channel is None:
                continue
            ids = db.column("SELECT user_id FROM birthdays WHERE month = ? AND day = ? AND guild_id = ?",
                            month, day, guild.id)

            for uid in ids:
                user: User = self.bot.get_user(uid)
                if user is None:
                    user: User = await self.bot.fetch_user(uid)
                if user is not None:
                    await channel.send(f"Alles Gute {user.mention}!")


def setup(bot):
    bot.add_cog(Birthdays(bot))
