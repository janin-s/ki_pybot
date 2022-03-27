from discord.ext.commands import Cog, command
from discord import NotFound, HTTPException


class React(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("react")

    @command()
    async def react(self, ctx, reaction, message_id=0):
        if not chars_unique(reaction):
            await ctx.send("Uncooles Wort, KI will nicht <:sad2:731291939571499009>")
            return
        if message_id != 0:
            try:
                message = await ctx.fetch_message(message_id)
            except NotFound:
                await ctx.send(f"Message {message_id} weg, oh no :(")
                return
        else:
            try:
                message = await ctx.channel.history(limit=1, before=ctx.channel.last_message).get()
            except HTTPException:
                await ctx.send("message weg, oh no")
                return

        await ctx.message.delete()

        if len(message.reactions) + len(reaction) > 20:
            await ctx.send("Zu viel :(", delete_after=10)
            return

        for letter in list(reaction):
            unicode_id = get_unicode_id(letter)
            await message.add_reaction(unicode_id)


def chars_unique(s):
    checker = 0
    num_checker = 0
    special = {
        63: False,
        33: False,
        43: False,
        45: False
    }
    s = s.lower()
    for c in s:
        ascii_value = ord(c)
        # letters
        if 97 <= ascii_value <= 122:
            val = ascii_value - ord('a')
            # If bit corresponding to current
            # character is already set
            if (checker & (1 << val)) > 0:
                return False
            # set bit in checker
            checker |= (1 << val)

        # numbers
        elif 48 <= ascii_value <= 57:
            val1 = ascii_value - ord('0')
            # If bit corresponding to current
            # character is already set
            if (num_checker & (1 << val1)) > 0:
                return False
            # set bit in checker
            num_checker |= (1 << val1)

        # special
        elif ascii_value in special:
            if special[ascii_value]:
                return False
            special[ascii_value] = True

        else:
            return False
    return True


def get_unicode_id(c):
    c = c.lower()
    o = ord(c)
    if 97 <= o <= 122:
        return chr(127462 + (o - 97))
    if 48 <= o <= 57:
        return c + chr(65039) + chr(8419)
    if o == 63:
        return '\U00002753'
    if o == 33:
        return '\U00002757'
    if o == 43:
        return '\U00002795'
    if o == 45:
        return '\U00002796'
    return '\U00002753'


def setup(bot):
    bot.add_cog(React(bot))
