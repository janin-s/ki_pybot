import discord
import discord.ext
from discord.ext.commands import Cog, command, Context


class React(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("say")

    @command()
    async def say(self, ctx: Context, user_id_mention: str, *, content):
        user: discord.User = await get_user_from_id_or_mention(ctx, user_id_mention)

        nick: str = user.nick if isinstance(user, discord.Member) and user.nick is not None else user.display_name

        avatar_bytes: bytes = await user.avatar_url.read()

        guild_webhooks: list[discord.Webhook] = await ctx.guild.webhooks()
        webhooks_filtered: list[discord.Webhook] = [w for w in guild_webhooks if 'say-cmd-hook' in w.name]
        if not webhooks_filtered:
            webhook: discord.Webhook = await ctx.channel.create_webhook(name=f'say-cmd-hook', avatar=avatar_bytes)
        else:
            webhook: discord.Webhook = webhooks_filtered[0]

        await webhook.send(content=content, username=nick, avatar_url=user.avatar_url)


async def get_user_from_id_or_mention(ctx: Context, user_id_mention: str) -> discord.User:
    if user_id_mention.isnumeric():
        user: discord.User = ctx.guild.get_member(user_id_mention)
        if not user:
            user: discord.User = await ctx.guild.fetch_member(user_id_mention)
    else:
        mentions: list[discord.User] = ctx.message.mentions
        user: discord.User = mentions[0] if mentions else ctx.author
    return user


def setup(bot):
    bot.add_cog(React(bot))
