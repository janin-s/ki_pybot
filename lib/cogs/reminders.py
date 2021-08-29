import asyncio

from apscheduler.jobstores.base import JobLookupError
from discord import User, Embed
from discord.ext.commands import *
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

from ..utils import send_paginated, parse_datetime
from lib.db import db
from dateutil import parser
from datetime import datetime, timedelta


class Reminders(Cog):
    def __init__(self, bot):
        self.bot = bot
        # delete invalid reminders in the past
        db.execute('DELETE FROM reminders WHERE time < ?', datetime.now().isoformat())
        jobs = self.bot.scheduler.get_jobs()
        record = db.record(
                    'SELECT reminder_id, job_id, time FROM reminders WHERE time=(SELECT min(time) FROM reminders)')
        # add job if there is an upcoming reminder and either no jobs or no job_id fitting the upcoming reminder
        if record is not None and (jobs is None or len(jobs) == 0 or record[1] not in [job.id for job in jobs]):
            job = self.bot.scheduler.add_job(self.reminder_call, 'date', run_date=datetime.fromisoformat(record[2]))
            # update job id for the upcoming reminder that just was scheduled
            db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', job.id, record[0])

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reminders")

    @command(aliases=['reminder', 'remindme'])
    async def reminders(self, ctx, datestring=None, *, message='reminding you :)'):
        """reminder: !remindme DD.MM[.YYYY][;HH:MM] reminds the calling user"""
        if datestring is None:
            await reminder_info(ctx)
            return
        # parse the date
        try:
            time: datetime = parse_datetime(datestring)
        except ValueError:
            await ctx.send("invalid date format")
            return
        if time < datetime.now():
            return

        # fetch the next upcoming reminder to check if the new one is earlier
        record = db.record('''SELECT reminder_id, job_id, time FROM reminders WHERE time = 
                         (SELECT min(time) FROM reminders)''')
        if record is not None:
            next_reminder_id, next_reminder_job_id, next_rmd_time = record
        else:
            next_reminder_id, next_reminder_job_id, next_rmd_time = [0, "", datetime.max.isoformat()]

        new_job_id = ""
        # if the new reminder is the earliest remove the current scheduled job otherwise don't create now job
        if time.isoformat() < next_rmd_time or next_reminder_job_id == "" or next_rmd_time < datetime.now().isoformat():
            if next_reminder_job_id != "":
                # remove the job of the old earliest reminder if there is such a reminder and set the job_id to ""
                try:
                    self.bot.scheduler.remove_job(next_reminder_job_id)
                except JobLookupError:
                    pass  # TODO maybe better error handling
                db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', "", next_reminder_id)
            # add the job for the new earliest reminder
            new_job: Job = self.bot.scheduler.add_job(self.reminder_call, 'date', run_date=time)
            new_job_id = new_job.id
        user_mentions_string = " ".join([user.mention for user in [ctx.message.author] + ctx.message.mentions])
        role_mentions_string = " ".join([role.mention for role in ctx.message.role_mentions])

        db.execute('INSERT INTO reminders (job_id, user_id, guild_id, time, message, mentions) VALUES (?,?,?,?,?,?)',
                   new_job_id,
                   ctx.message.author.id,
                   ctx.guild.id,
                   time.isoformat(),
                   message,
                   " ".join([user_mentions_string, role_mentions_string]).strip())
        await ctx.send("Ich sag dann Bescheid")

    # sends the reminder, removes the sent reminder from the DB, adds a job for the next reminder & updates ots job_id
    async def reminder_call(self):
        # fetch the next upcoming reminder
        record = db.record('''SELECT reminder_id, job_id, user_id, guild_id, message, mentions FROM reminders WHERE time = 
                              (SELECT min(time) FROM reminders)''')
        if record is None:
            return
        reminder_id, job_id, user_id, guild_id, message, mentions = record
        if job_id != "":
            # fetch the user/channel to ping/send to, send the message and delete the corresponding reminder from the DB
            user = await self.bot.fetch_user(user_id)
            channel_id = db.field('SELECT reminder_channel FROM server_info WHERE guild_id = ?', guild_id)
            channel = await self.bot.fetch_channel(channel_id)
            print(f'user:{user}, channel:{channel}')
            if user is not None and channel is not None:
                embed = Embed(title='Reminder', description=message)
                await channel.send(mentions, embed=embed)
            print('deleting reminder')
            db.execute('DELETE FROM reminders WHERE reminder_id = ?', reminder_id)
        # fetch the next upcoming reminder and create a new scheduler job for it
        record2 = db.record('SELECT reminder_id, time FROM reminders WHERE time = (SELECT min(time) FROM reminders)')
        if record2 is None:
            return
        new_reminder_id, new_reminder_time = record2
        time = datetime.fromisoformat(new_reminder_time)
        new_job: Job = self.bot.scheduler.add_job(self.reminder_call, 'date', run_date=time)
        # update the job id for the upcoming reminder
        db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', new_job.id, new_reminder_id)


async def reminder_info(ctx):
    embed = Embed(title='Reminders')
    embed.add_field(name='aliases', value='You can use !reminders, !reminder or !remindme')
    embed.add_field(name='usage', value='Use !remindme <date> <message> to get a reminder on the specified date/time')
    embed.add_field(name='mentions', value='Every user or role mentioned in the message will be pinged by the reminder')
    embed.add_field(name='date',
                    value='Use MM.DD[.YYYY][;HH:MM] or \'today/heute\' and \'tomorrow/morgen\'')
    embed.set_thumbnail(
        url="https://pngimg.com/uploads/alarm_clock/alarm_clock_PNG2.png")
    await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Reminders(bot))
