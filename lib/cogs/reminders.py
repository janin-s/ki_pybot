import asyncio

from discord import User, Embed
from discord.ext.commands import *
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

from ..utils import send_paginated, parse_date, parse_reminder
from lib.db import db
from dateutil import parser
from datetime import datetime, timedelta


class Reminders(Cog):
    def __init__(self, bot):
        self.bot = bot
        # TODO delete reminders in the past

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reminders")

    @command(aliases=['reminder', 'remindme'])
    async def reminders(self, ctx, datestring, *, message):
        """reminder: !remindme DD.MM[.YYYY][;HH:MM] reminds the calling user"""
        # parse the date
        try:
            time: datetime = parse_reminder(datestring)
        except ValueError:
            await ctx.send("invalid date format")
            return
        if time < datetime.now():
            return

        # fetch the next upcoming reminder to check if the new one is earlier
        record = db.record('''SELECT reminder_id, job_id, time FROM reminders WHERE time = 
                         (SELECT min(time) FROM reminders)''')
        if record is not None:
            next_reminder_id, next_reminder_job_id, next_reminder_time = record
        else:
            next_reminder_id, next_reminder_job_id, next_reminder_time = [0, "", datetime.max.isoformat()]

        new_job_id = ""
        # if the new reminder is the earliest remove the current scheduled job otherwise don't create now job
        if time.isoformat() < next_reminder_time:
            if next_reminder_job_id != "":
                # remove the job of the old earliest reminder if there is such a reminder and set the job_id to ""
                self.bot.scheduler.remove_job(next_reminder_job_id)
                db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', "", next_reminder_id)
            # add the job for the new earliest reminder
            new_job: Job = self.bot.scheduler.add_job(self.reminder_call, 'date', run_date=time, args=[ctx])
            new_job_id = new_job.id

        db.execute('INSERT INTO reminders (job_id, user_id, guild_id, time, message) VALUES (?, ?,?,?,?)',
                   new_job_id,
                   ctx.message.author.id,
                   ctx.guild.id,
                   time.isoformat(),
                   message)
        await ctx.send("Ich sag dann bescheid")

    # sends the reminder, removes the sent reminder from the DB, adds a job for the next reminder & updates ots job_id
    async def reminder_call(self, ctx):
        # fetch the next upcoming reminder
        record = db.record('''SELECT reminder_id, job_id, user_id, guild_id, message FROM reminders WHERE time = 
                              (SELECT min(time) FROM reminders)''')
        if record is None:
            return
        reminder_id, job_id, user_id, guild_id, message = record
        if job_id != "":
            # fetch the user/channel to ping/send to, send the message and delete the corresponding reminder from the DB
            user = await self.bot.fetch_user(user_id)
            channel_id = db.field('SELECT reminder_channel FROM server_info WHERE guild_id = ?', guild_id)
            channel = await self.bot.fetch_channel(channel_id)
            print(f'user:{user}, channel:{channel}')
            if user is not None and channel is not None:
                embed = Embed(title='Reminder', description=message)
                await channel.send(user.mention, embed=embed)
            print('deleting reminder')
            db.execute('DELETE FROM reminders WHERE reminder_id = ?', reminder_id)
        # fetch the next upcoming reminder and create a new scheduler job for it
        record2 = db.record('SELECT reminder_id, time FROM reminders WHERE time = (SELECT min(time) FROM reminders)')
        if record2 is None:
            return
        new_reminder_id, new_reminder_time = record2
        time = datetime.fromisoformat(new_reminder_time)
        new_job: Job = self.bot.scheduler.add_job(self.reminder_call, 'date', run_date=time, args=[ctx])
        # update the job id for the upcoming reminder
        db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', new_job.id, new_reminder_id)


def setup(bot):
    bot.add_cog(Reminders(bot))
