from random import choice
from discord.ext.commands import Cog, command, has_permissions

from lib.bot import Bot
from lib.db import db
from lib.utils import utils

REPLACE_SENDER = "[$SENDER$]"
REPLACE_MENTIONS = "[$MENTIONS$]"


class Msg(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("msg")

    @command(name="msg", aliases=["message"])
    async def msg(self, ctx):
        all_msgs = db.column("SELECT DISTINCT shorthand FROM messages WHERE guild_id = ?", ctx.guild.id)
        if len(all_msgs) <= 0:
            await ctx.send("No shorthands available.")
            return

        text = "Available shorthands:\n" + "\n".join(sorted(all_msgs))

        await utils.send_paginated(ctx, start="```", end="```", content=text)

    @command(name="set_message")
    @has_permissions(administrator=True)
    async def add_message(self, ctx, name, *, content):
        """assigns content to a shorthand"""
        # TODO: clean content
        print(f'adding message {name} to DB')
        db.execute('''INSERT OR REPLACE INTO messages (shorthand, message, guild_id) VALUES (?, ?, ?)''',
                   name, content, ctx.guild.id)
        await ctx.message.add_reaction('\U00002705')


async def message(ctx, msg=""):
    print(f"message with shorthand {msg}.")
    if msg == "" or ctx is None:
        return
    guild_id = ctx.guild.id

    msgs = db.column("SELECT message FROM messages WHERE guild_id = ? AND shorthand = ?", guild_id, msg)

    if msgs is not None and len(msgs) != 0:
        msg = choice(msgs)
        msg = str(msg)
        if REPLACE_SENDER in msg:
            msg = msg.replace(REPLACE_SENDER, ctx.message.author.display_name)
        if REPLACE_MENTIONS in msg:
            msg = msg.replace(REPLACE_MENTIONS, "".join([", "+m.display_name for m in ctx.message.mentions])[2:])

        await ctx.send(msg.replace("\\n", "\n"))
    else:
        raise utils.MsgNotFound


def setup(bot):
    bot.add_cog(Msg(bot))
