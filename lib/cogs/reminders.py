import asyncio

from apscheduler.jobstores.base import JobLookupError
from discord import User, Embed
from discord.ext.commands import *
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

from ..utils import send_paginated, parse_datetime
from lib.db import db
from datetime import datetime, timedelta


class Reminders(Cog):
    def __init__(self, bot):
        self.bot = bot
        # delete invalid reminders in the past
        db.execute('DELETE FROM reminders WHERE time < ?', datetime.now().isoformat())
        jobs = self.bot.scheduler.get_jobs()
        record = db.record(
            '''SELECT reminder_id, job_id, time FROM reminders WHERE
            time=(SELECT min(time) FROM reminders WHERE time > ?)''',
            datetime.now().isoformat())
        # add job if there is an upcoming reminder and either no jobs or no job_id fitting the upcoming reminder
        if record is not None and (jobs is None or len(jobs) == 0 or record[1] not in [job.id for job in jobs]):
            job = self.bot.scheduler.add_job(func=self.reminder_call, trigger='date',
                                             args=[record[0]],
                                             run_date=datetime.fromisoformat(record[2]))
            # update job id for the upcoming reminder that just was scheduled
            db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', job.id, record[0])

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reminders")

    @group(aliases=['reminder', 'remindme', 'rm'], invoke_without_command=True)
    async def reminders(self, ctx):
        """reminder: !reminder add DD.MM[.YYYY][;HH:MM] reminds the calling user"""
        embed = Embed(title='Reminders')
        embed.add_field(name='aliases', value='You can use !reminders, !reminder, !remindme or !rm')
        embed.add_field(name='usage',
                        value='Use !rm add <date> [<message>] to get a reminder on the specified date/time')
        embed.add_field(name='list',
                        value='Use !rm list [<mentions>] to get a list of reminders for the mentioned users '
                              '(all users when nobody mentioned)')
        embed.add_field(name='snooze',
                        value='User !rm snooze [x](h/m) or !snooze [x](h/m) to let your last reminder snooze for x '
                              'hours/minutes, alias is schlummer[n]')
        embed.add_field(name='mentions',
                        value='Every user or role mentioned in the message will be pinged by the reminder')
        embed.add_field(name='date',
                        value='Use DD.MM[.YYYY][;HH:MM] or \'today/heute[;HH:MM]\' and \'tomorrow/morgen[;HH:MM]\'')
        embed.set_thumbnail(
            url="https://pngimg.com/uploads/alarm_clock/alarm_clock_PNG2.png")
        await ctx.send(embed=embed)
        return

    @reminders.command()
    async def add(self, ctx, datestring=None, *, message='reminding you :)'):
        """add reminder"""
        # parse the date
        try:
            time: datetime = parse_datetime(datestring)
        except ValueError:
            await ctx.send("invalid date format")
            return
        if time < (datetime.now() + timedelta(minutes=1)):
            if datetime.now() - time > timedelta(hours=datetime.now().hour):
                await ctx.send("des leider schon vorbei :(")
                return
            print(f'time b4 update {time}')
            time = time + timedelta(days=1)
            print(f'time after update {time}')

        # fetch the next upcoming reminder to check if the new one is earlier

        user_mentions_string = " ".join([user.mention for user in [ctx.message.author] + ctx.message.mentions])
        role_mentions_string = " ".join([role.mention for role in ctx.message.role_mentions])

        new_reminder_id = db.field(
            'INSERT INTO reminders (job_id, user_id, guild_id, time, message, mentions) VALUES '
            '(?,?,?,?,?,?) RETURNING reminder_id',
            '',
            ctx.message.author.id,
            ctx.guild.id,
            time.isoformat(),
            message,
            " ".join([user_mentions_string, role_mentions_string]).strip())

        if new_reminder_id is None:
            print('hilfeeee')
            return
        new_job_id = await self.update_upcoming_job(time, new_reminder_id)

        if new_job_id is not None:
            db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', new_job_id, new_reminder_id)

        await ctx.send("Ich sag dann Bescheid")

    @reminders.command()
    async def list(self, ctx):
        mentioned_ids = [user.id for user in ctx.message.mentions]
        if mentioned_ids is None or len(mentioned_ids) == 0:
            reminders = db.records('SELECT user_id, time, message FROM reminders WHERE guild_id = ? ORDER BY time',
                                   ctx.guild.id)
        else:
            var_list = '?,' * (len(mentioned_ids) - 1) + '?'
            reminders = \
                db.records(
                    f'SELECT user_id, time, message FROM reminders WHERE guild_id = ? AND user_id IN ({var_list}) '
                    f'ORDER BY time',
                    ctx.guild.id, *mentioned_ids)
        if reminders is None or len(reminders) == 0:
            await ctx.send('no reminders found')
            return
        rems = ''
        for uid, time, message in reminders:
            user = ctx.guild.get_member(uid)
            if user is None:
                user = await self.bot.fetch_user(uid)
            rems += f'{datetime.fromisoformat(time).strftime("%d.%m.%Y %H:%M")}, {user.display_name}: {message}\n'
        await send_paginated(ctx, start="```", end="```", content=rems)

    # sends the reminder, removes the sent reminder from the DB, adds a job for the next reminder & updates ots job_id
    async def reminder_call(self, reminder_id: int):
        print(f'reminder call for reminder {reminder_id}')
        # fetch the next upcoming reminder
        record = db.record('''SELECT reminder_id, user_id, guild_id, message, mentions, time FROM reminders WHERE 
                                reminder_id = ?''', reminder_id)
        if record is None or len(record) != 6:
            print(f'faulty record {record}')
            return
        reminder_id, user_id, guild_id, message, mentions, time = record

        # fetch the user/channel to ping/send to, send the message and delete the corresponding reminder from the DB
        user = await self.bot.fetch_user(user_id)
        channel_id = db.field('SELECT reminder_channel FROM server_info WHERE guild_id = ?', guild_id)
        channel = await self.bot.fetch_channel(channel_id)

        if user is not None and channel is not None:
            embed = Embed(title='Reminder', description=message)
            await channel.send(mentions, embed=embed)
        delete_job: Job = self.bot.scheduler.add_job(func=delete_reminder,
                                                     trigger='date',
                                                     args=[reminder_id],
                                                     run_date=(datetime.now() + timedelta(hours=1)))

        db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', delete_job.id, reminder_id)
        # fetch the next upcoming reminder (next reminder with time >= time of this reminder, which is not this one and
        # which has no delete job (last one needed for multiple reminders at same time)
        record2 = db.record(r"""SELECT reminder_id, time FROM reminders WHERE 
                                time = (SELECT min(time) FROM reminders WHERE time >= ? AND reminder_id != ?) AND 
                                reminder_id != ? AND 
                                job_id = '' """, time, reminder_id, reminder_id)

        if record2 is None:
            print(f'no upcoming reminder found for current time {time} and current id {reminder_id}')
            return
        new_reminder_id, new_reminder_time_iso = record2
        new_time = datetime.fromisoformat(new_reminder_time_iso)
        if new_time <= datetime.now():
            print(f'shortcut for new time {new_time} and current time {datetime.now().isoformat()}')
            await self.reminder_call(new_reminder_id)
            return
        new_job: Job = self.bot.scheduler.add_job(func=self.reminder_call, trigger='date',
                                                  args=[new_reminder_id],
                                                  run_date=new_time)
        print(f'added job {new_job.id} for next reminder {new_reminder_id} after reminder call for time {new_time}')
        # update the job id for the upcoming reminder
        db.execute('UPDATE reminders SET job_id = ? WHERE reminder_id = ?', new_job.id, new_reminder_id)

    @command(aliases=['schlummer', 'schlummern'])
    async def snooze(self, ctx, time=''):
        await self.do_snooze(ctx, time)

    @reminders.command(aliases=['snooze', 'schlummer', 'schlummern'])
    async def do_snooze(self, ctx, time=None):
        # parse time
        if time is None or time == '':
            date = datetime.now() + timedelta(minutes=10)
        else:
            try:
                if 'h' in time:
                    hours = float(time[:-1])
                    date = datetime.now() + timedelta(hours=hours)
                elif 'm' in time:
                    minutes = float(time[:-1])
                    date = datetime.now() + timedelta(minutes=minutes)
                else:
                    date = datetime.now() + timedelta(minutes=float(time))
            except ValueError:
                await ctx.send('invalid time string :(')
                return

        user_id = ctx.message.author.id
        record = db.record('''SELECT reminder_id, job_id FROM reminders WHERE
                                user_id = ? AND
                                time = (SELECT max(time) FROM reminders WHERE time < ?)''',
                           user_id, datetime.now().isoformat())
        if record is None:
            await ctx.send("No reminder to snooze!")
            return
        reminder_id, job_id = record
        # remove job for deleting snoozed reminder
        self.bot.scheduler.remove_job(job_id)

        # check if snoozed reminder is the new upcoming and if yes add job
        new_job_id = await self.update_upcoming_job(date, reminder_id)
        if new_job_id is None:
            new_job_id = ''

        db.execute('''UPDATE reminders SET job_id = ?, time = ? WHERE reminder_id = ?''',
                   new_job_id, date.isoformat(), reminder_id)
        await ctx.send(f'Set reminder time to {date.strftime("%d.%m.%Y %H:%M")}!')

    # if the new_time is the new upcoming reminder, remove the old upcoming job and add a new one
    # returns the new job id for the upcoming job or None if new_time is not the upcoming reminder
    async def update_upcoming_job(self, new_time: datetime, reminder_id: int):
        # get upcoming reminder
        next_reminder = db.record('''SELECT reminder_id, job_id, time FROM reminders WHERE time = 
                                     (SELECT min(time) FROM reminders WHERE time > ? AND reminder_id != ?)''',
                                  datetime.now().isoformat(), reminder_id)
        if next_reminder is not None:
            next_reminder_id, next_reminder_job_id, next_rmd_time = next_reminder
        else:
            next_reminder_id, next_reminder_job_id, next_rmd_time = ("", 0, "999")

        if next_reminder is None or new_time.isoformat() < next_rmd_time or next_reminder_job_id == "":
            if next_reminder_job_id != "" and next_reminder_job_id != 0:
                try:
                    self.bot.scheduler.remove_job(next_reminder_job_id)
                    print(f'removed job {next_reminder_job_id} for reminder with id {next_reminder_id}')
                except JobLookupError:
                    print(f'joblookuperror for id {next_reminder_job_id}')
                    pass  # TODO maybe better error handling

            db.execute(r"UPDATE reminders SET job_id = '' WHERE reminder_id = ?", next_reminder_id)
            # add the job for the new earliest reminder
            new_job: Job = self.bot.scheduler.add_job(func=self.reminder_call, trigger='date',
                                                      args=[reminder_id],
                                                      run_date=new_time)
            new_job_id = new_job.id
            print(f'added new job at {new_time.isoformat()} with id {new_job_id} for reminder {reminder_id}')
            # update new upcoming reminder
            return new_job_id
        return None


async def delete_reminder(reminder_id: int):
    print(f'deleting reminder {reminder_id}')
    db.execute('DELETE FROM reminders WHERE reminder_id = ?', reminder_id)
    return


def setup(bot):
    bot.add_cog(Reminders(bot))
