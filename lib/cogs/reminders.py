
from dataclasses import dataclass

from discord import Embed
from discord.ext import tasks
from discord.ext.commands import *

from ..utils import send_paginated, parse_datetime
from lib.db import db
from datetime import datetime, timedelta


@dataclass()
class Reminder:
    reminder_id: int
    user_id: int
    guild_id: int
    time: datetime
    message: str
    mentions: str
    called: bool


class Reminders(Cog):

    def __init__(self, bot):
        self.bot = bot

        records = db.records('SELECT reminder_id, user_id, guild_id, time, message, mentions, called FROM reminders')
        self.reminders: [Reminder] = [Reminder(reminder_id=reminder_id,
                                               user_id=user_id,
                                               guild_id=guild_id,
                                               time=datetime.fromisoformat(time),
                                               message=message,
                                               mentions=mentions,
                                               called=called)
                                      for (reminder_id, user_id, guild_id, time, message, mentions, called) in records]
        self.reminder_loop.start()
        self.delete_reminders.start()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reminders")

    def cog_unload(self):
        self.reminder_loop.cancel()

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
                        value='Use only time as HH:MM, sets reminder on next occurrence of this time. For dates use '
                              'DD.MM[.YYYY][;HH:MM] or \'today/heute[;HH:MM]\' and \'tomorrow/morgen[;HH:MM]\'')
        embed.set_thumbnail(
            url="https://pngimg.com/uploads/alarm_clock/alarm_clock_PNG2.png")
        await ctx.send(embed=embed)
        return

    @reminders.command()
    async def list(self, ctx):
        mentioned_ids = [user.id for user in ctx.message.mentions]
        if mentioned_ids is None or len(mentioned_ids) == 0:
            reminders = self.reminders
        else:
            reminders = list(filter(lambda r: r.user_id in mentioned_ids, self.reminders))
        if reminders is None or len(reminders) == 0:
            await ctx.send('no reminders found')
            return
        reminders = sorted(reminders, key=lambda r: r.time)
        rems = ''
        for rem in reminders:
            user = ctx.guild.get_member(rem.user_id)
            if user is None:
                user = await self.bot.fetch_user(rem.user_id)
            rems += f'{rem.time.strftime("%d.%m.%Y %H:%M")}, {user.display_name}: {rem.message}\n'
        await send_paginated(ctx, start="```", end="```", content=rems)

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
            # if datetime.now() - time > timedelta(hours=datetime.now().hour):
            #     await ctx.send("des leider schon vorbei :(")
            #     return
            time = time + timedelta(days=1)

        user_mentions_string = " ".join([user.mention for user in [ctx.message.author] + ctx.message.mentions])
        role_mentions_string = " ".join([role.mention for role in ctx.message.role_mentions])
        rem = Reminder(reminder_id=-1,
                       user_id=ctx.message.author.id,
                       guild_id=ctx.guild.id,
                       time=time,
                       message=message,
                       mentions=" ".join([user_mentions_string, role_mentions_string]).strip(),
                       called=False)
        rem_id = insert_reminder(rem)
        rem.reminder_id = rem_id

        self.reminders.append(rem)

        await ctx.send("Ich sag dann Bescheid")

    # to use !snooze and !rm snooze
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

        reminder_id = db.field('''SELECT reminder_id FROM reminders WHERE
                                user_id = ? AND
                                time = (SELECT max(time) FROM reminders WHERE time < ? AND user_id = ?)''',
                               user_id, datetime.now().isoformat(), user_id)

        if reminder_id is None:
            await ctx.send("No reminder to snooze!")
            return

        db.execute('''UPDATE reminders SET time = ?, called = ? WHERE reminder_id = ?''',
                   date.isoformat(), False, reminder_id)
        for rem in self.reminders:
            if rem.reminder_id == reminder_id:
                rem.called = False
                rem.time = date
        await ctx.send(f'Set reminder time to {date.strftime("%d.%m.%Y %H:%M")}!')

    @tasks.loop(minutes=10)
    async def delete_reminders(self):
        cutoff = datetime.now() - timedelta(hours=1)
        db.execute('DELETE FROM reminders WHERE time <= ?', cutoff.isoformat())

        self.reminders = list(filter(lambda r: r.time <= cutoff, self.reminders))

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        # fetch the next upcoming reminder
        records = db.records('''SELECT reminder_id, guild_id, message, mentions FROM reminders WHERE 
                                time <= ? AND called= ?''', (datetime.now() + timedelta(seconds=15)).isoformat(), False)
        for reminder_id, guild_id, message, mentions in records:
            channel_id = db.field('SELECT reminder_channel FROM server_info WHERE guild_id = ?', guild_id)
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(channel_id)
            embed = Embed(title='Reminder', description=message)
            await channel.send(mentions, embed=embed)

        ids = [reminder_id for reminder_id, _, _, _ in records]
        for rem_id in ids:
            db.execute('''UPDATE reminders SET called = ? WHERE reminder_id = ?''',
                       True, rem_id)
            for rem in self.reminders:
                if rem.reminder_id == rem_id:
                    rem.called = True

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()


def insert_reminder(rem: Reminder) -> int:
    new_reminder_id: int = db.field(
        'INSERT INTO reminders (user_id, guild_id, time, message, mentions) VALUES '
        '(?,?,?,?,?) RETURNING reminder_id',
        rem.user_id,
        rem.guild_id,
        rem.time.isoformat(),
        rem.message,
        rem.mentions)
    return new_reminder_id


def setup(bot):
    bot.add_cog(Reminders(bot))
