from discord.ext.commands import *
from re import search
from ..db import db
from ..utils import MsgNotFound

REPLACE_SENDER = "[$SENDER$]"
REPLACE_MENTIONS = "[$MENTIONS$]"


class Msg(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("msg")

    @command(name="msg", aliases=["message"])
    async def msg(self, ctx):
        all_msgs = db.execute("SELECT shorthand FROM messages WHERE guild_id = ?", ctx.guild.id)
        if len(all_msgs) <= 0:
            await ctx.send("No shorthands available.")
            return

        text = ""

        for row in all_msgs:
            text += f"`{row[0]}`\n"

        await ctx.send(f"Available shorthands:\n{text}")


async def message(ctx, message=""):

    if message == "" or ctx is None:
        return
    guild_id = ctx.guild.id

    msgs = db.column("SELECT message FROM messages WHERE guild_id = ? AND shorthand = ?", guild_id, message)

    for msg in msgs:
        if msg is not None:
            msg = str(msg)
            if REPLACE_SENDER in msg:
                msg = msg.replace(REPLACE_SENDER, ctx.message.author.display_name)
            if REPLACE_MENTIONS in msg:
                msg = msg.replace(REPLACE_MENTIONS, "".join([", "+m.display_name for m in ctx.message.mentions])[2:])
            await ctx.send(msg)
        else:
            raise MsgNotFound


def setup(bot):
    bot.add_cog(Msg(bot))
