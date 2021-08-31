from datetime import datetime, timedelta

import discord
from discord import Member
from discord.ext.commands import *
from discord.ext import commands

from lib.db import db

OFFLINE_PUNISH = True
PUNISH_INTERVAL = timedelta(hours=12)


class DMCmds(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("dm_cmds")

    @command(name="hug")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hug(self, ctx):
        """umarmt alle mentioned user privat. 1 min cooldown"""
        users = ctx.message.mentions
        for user in users:
            current_id = user.id
            if current_id == 709865255479672863:
                user = ctx.message.author
                sender = "KI"
                await ctx.send("KI hat dich auch lieb! :)")
            else:
                sender = ctx.message.author.display_name
            await ctx.send(f"{sender} versendet eine Umarmung an {user.display_name}!")

            dm_channel = user.dm_channel
            try:
                if dm_channel is None:
                    dm_channel = await user.create_dm()
                await dm_channel.send(f"Liebe! {sender} sendet dir eine Umarmung!")
                await dm_channel.send("https://i.pinimg.com/originals/e2/f7/2a/e2f72a771865ea0d74895cb2c2199a83.gif")
            except discord.Forbidden:
                pass
        await ctx.message.delete()

    @command(name="punish")
    async def punish(self, ctx):
        """"bestraft alle mentioned user"""
        users = ctx.message.mentions
        for user in users:
            current_id = user.id
            if current_id == ctx.bot.user.id:
                user = ctx.message.author
                await ctx.send("KI schlägt zurück")
            elif not OFFLINE_PUNISH and user.status is discord.Status.offline:
                await ctx.send("offline user puishen sehr fies :(")
                continue
            else:
                sql_get_time = "SELECT punish_time FROM punish_times WHERE guild_id = ? AND user_id = ?"
                last_punish_string = db.field(sql_get_time, ctx.guild.id, current_id)

                if last_punish_string is None:
                    last_punish = datetime.min
                else:
                    try:
                        last_punish = datetime.fromisoformat(last_punish_string)
                    except ValueError:
                        last_punish = datetime.min

                if (datetime.now() - last_punish) < PUNISH_INTERVAL:
                    await ctx.send(f"{user.display_name} wurde vor kurzem erst bestraft!")
                    continue
            sql_update_time = """\
            INSERT INTO punish_times (user_id, guild_id, punish_time) 
            VALUES (?,?,?) 
            ON CONFLICT (user_id, guild_id) DO
            UPDATE SET punish_time = ? WHERE user_id = ? AND guild_id = ?"""
            time = datetime.now().isoformat(timespec='seconds')
            db.execute(sql_update_time, current_id,  ctx.guild.id, time, time, current_id, ctx.guild.id)
            await kick_invite_roles(ctx, user, ctx.guild)

    @command(name='votekick')
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def votekick(self, ctx):
        # TODO implement votekick with scheduled reset and database
        pass


async def kick_invite_roles(ctx, user, guild):
    records = [(r.id, user.id, guild.id) for r in user.roles]
    if isinstance(user, Member) and user.nick is not None:
        nick = user.nick
    else:
        nick = user.display_name
    print(f'kicking user {user.id} with nick {nick} from guild {guild.id}')
    insert_roles = "REPLACE INTO roles(role_id, user_id, guild_id) VALUES (?, ?, ?)"
    db.multiexec(insert_roles, records)

    db.execute('REPLACE INTO users (display_name, id, guild_id) VALUES (?,?,?)',
               str(nick), user.id, guild.id)

    dm_channel = user.dm_channel
    await ctx.send(f"{nick} soll sich schämen gehen")
    invite = await ctx.channel.create_invite(max_uses=1)
    try:
        if dm_channel is None:
            dm_channel = await user.create_dm()
        await dm_channel.send("shame!\n" * 4)
        await dm_channel.send("https://media.giphy.com/media/vX9WcCiWwUF7G/giphy.gif")
        await dm_channel.send(invite.url)
    except discord.Forbidden:
        await ctx.send("da ist jemand ehrenlos und hat bot dms aus. >:(")
    try:
        await user.kick(reason="punish")
    except discord.Forbidden:
        await ctx.send("KI nicht mächtig genug :(")


def setup(bot):
    bot.add_cog(DMCmds(bot))
