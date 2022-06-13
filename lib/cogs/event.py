from datetime import datetime, timedelta
from discord import Role, Embed, Message, ScheduledEvent, RawScheduledEventSubscription, Guild, RawMessageDeleteEvent, \
    NotFound
from discord.ext.commands import Cog, group, Context
from lib.bot import Bot
from lib.db import db
from lib.utils import utils
from lib.utils.event_classes import Event, EventButton, EventView


class EventCog(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        records = db.records(
            'SELECT guild_id, channel_id, message_id, event_id, role_id FROM events WHERE start_time > ?',
            datetime.now().isoformat())
        for guild_id, channel_id, mid, event_id, role_id in records:
            guild = await self.bot.fetch_guild(guild_id)
            channel = await guild.fetch_channel(channel_id)
            message = await channel.fetch_message(mid)

            role = guild.get_role(role_id)
            if role:
                view = EventView()
                view.add_item(EventButton(role, event_id, mode='join'))
                view.add_item(EventButton(role, event_id, mode='leave'))
                await message.edit(view=view)
                self.bot.add_view(view, message_id=mid)

        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("event")

    @group(invoke_without_command=True)
    async def event(self, ctx):
        embed = Embed(title='Events')
        embed.add_field(name='Available commands', value='add & list')
        embed.add_field(
            name='Add Usage',
            value=f'{self.bot.command_prefix[0]}event add name;desc;start date;start time;end date;end time;place',
            inline=False)
        embed.add_field(name='Formats', value='name, desc, place: any text\n dates: YYYY-MM-DD\n times: HH:MM',
                        inline=False)
        start = datetime.now() + timedelta(minutes=30)
        end = start + timedelta(hours=2)
        example = f'{self.bot.command_prefix[0]}event add Essen;Essen gehen mit der Gang;' \
                  f'{start.strftime("%Y-%m-%d;%H:%M;")}{end.strftime("%Y-%m-%d;%H:%M;")}tolles Restaurant'
        embed.add_field(name='Example', value=example)
        await ctx.send(embed=embed)

    @event.command()
    async def add(self, ctx: Context, *, event: str):
        """!event add name;description;start date;start time;end date; end time; place"""
        args = event.split(';')
        if len(args) != 7:
            await ctx.send(f'Invalid number of arguments: {len(args)}')
            return
        name: str = args[0]
        description: str = args[1]
        place = args[6]
        try:
            start = datetime.strptime(args[2] + ';' + args[3], '%Y-%m-%d;%H:%M')
            end = datetime.strptime(args[4] + ';' + args[5], '%Y-%m-%d;%H:%M')
        except ValueError:
            await ctx.send(f'Couldn\'t parse date')
            return
        role_name = f'event-{"-".join(name.lower().split(" "))}'
        role: Role = await ctx.guild.create_role(name=role_name, mentionable=True)

        event = await ctx.guild.create_scheduled_event(name=name,
                                                       description=description,
                                                       start_time=start,
                                                       end_time=end,
                                                       location=place)

        event_id: int = db.field(
            'INSERT INTO '
            'events ('
            'guild_id, channel_id, message_id, event_id, role_id, name, description, start_time, end_time, location) '
            'VALUES (?,?,?,?,?,?,?,?,?,?)'
            'RETURNING id',
            ctx.guild.id, ctx.channel.id, -1, event.id, role.id, name, description, start, end, place)

        event_embed = create_event_embed(name, description, place, start, end)
        view = EventView()
        view.add_item(EventButton(role, event_id, mode='join'))
        view.add_item(EventButton(role, event_id, mode='leave'))

        message = await ctx.send(embed=event_embed, view=view)
        self.bot.add_view(view, message_id=message.id)
        db.execute('UPDATE events SET message_id = ? WHERE id = ?', message.id, event_id)

    @event.command()
    async def list(self, ctx: Context):
        records = db.records('SELECT * FROM events WHERE guild_id = ? ORDER BY start_time', ctx.guild.id)
        events = [str(tuple_to_event(t)) for t in records]

        await utils.send_paginated(ctx, start="```", end="```", content='\n'.join(events))

    @event.command()
    async def remove(self, ctx: Context, message_id: int):
        name: str | None = await self.delete_event(message_id=message_id)
        if not name:
            await ctx.send(f'Event not found')
        await ctx.send(f'Removed event {name}')

    @Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        message_id = payload.message_id
        record = db.record('SELECT * FROM events WHERE message_id = ?', message_id)
        if record:
            print(f'raw message delete found events')
            await self.delete_event(message_id=message_id, delete_message=False)

    @Cog.listener()
    async def on_scheduled_event_delete(self, event: ScheduledEvent):
        await self.delete_event(event_id=event.id, delete_scheduled_event=False)

    @Cog.listener()
    async def on_raw_scheduled_event_user_add(self, payload: RawScheduledEventSubscription):
        await self.handle_scheduled_event_user_change(payload)

    @Cog.listener()
    async def on_raw_scheduled_event_user_remove(self, payload: RawScheduledEventSubscription):
        await self.handle_scheduled_event_user_change(payload)

    async def handle_scheduled_event_user_change(self, payload: RawScheduledEventSubscription):
        user_id = payload.user_id
        event_id = payload.event_id
        guild: Guild = payload.guild
        member = guild.get_member(user_id)
        role_id = db.field('SELECT role_id FROM events WHERE event_id = ?', event_id)
        if not role_id:
            return
        role = guild.get_role(role_id)
        if payload.event_type == 'USER_ADD' and role:
            await member.add_roles(role, atomic=True)
        elif role:
            await member.remove_roles(role, atomic=True)

    async def delete_event(self, message_id: int = None, event_id: int = None,
                           delete_scheduled_event: bool | None = True, delete_message: bool | None = True):
        if message_id is None and event_id is None:
            raise ValueError
        if message_id is not None:
            query = f'SELECT * FROM events WHERE message_id = ?'
            value = message_id
        if event_id is not None:
            query = f'SELECT * FROM events WHERE event_id = ?'
            value = event_id

        record = db.record(query, value)
        if not record:
            return None

        event_id, guild_id, _, message_id, sched_event_id, role_id, name, _, _, _, _ = record
        guild = await self.bot.fetch_guild(guild_id)

        roles = [r for r in guild.roles if r.id == role_id]
        if roles:
            await roles[0].delete()

        message: Message | None = self.bot.get_message(message_id)
        if message and delete_message:
            await message.delete()

        if delete_scheduled_event:
            event: ScheduledEvent | None = await guild.fetch_scheduled_event(sched_event_id)
            if event:
                try:
                    await event.delete()
                except NotFound:
                    pass
        db.execute('DELETE FROM events WHERE id = ?', event_id)
        return name


def create_event_embed(name: str, description: str, place: str, start: datetime, end: datetime) -> Embed:
    embed = Embed(title=name, description=description)
    embed.add_field(name='When?', value=f'{start.strftime("%H:%M %d.%m.%y")} - {end.strftime("%H:%M %d.%m.%y")}')
    embed.add_field(name='Where?', value=place)
    return embed


def tuple_to_event(t: tuple) -> Event:
    return Event(*t[1:])


def setup(bot):
    bot.add_cog(EventCog(bot))
