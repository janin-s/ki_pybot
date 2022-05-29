from random import choice

from lib.db import db

REPLACE_SENDER = "[$SENDER$]"
REPLACE_MENTIONS = "[$MENTIONS$]"


class MsgNotFound(Exception):
    pass


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
            msg = msg.replace(REPLACE_MENTIONS, "".join([", " + m.display_name for m in ctx.message.mentions])[2:])

        await ctx.send(msg.replace("\\n", "\n"))
    else:
        raise MsgNotFound
