import discord
from discord.ext.commands import Cog, command, Context

from lib.bot import Bot


class Say(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("say")

    @command()
    async def say(self, ctx: Context, user: discord.Member, *, content):
        """'!say [mention | user_id] content' creates message containing content as the user from the first argument"""
        nick: str = user.nick if isinstance(user, discord.Member) and user.nick is not None else user.display_name

        guild_webhooks: list[discord.Webhook] = await ctx.guild.webhooks()
        webhooks_filtered: list[discord.Webhook] = [w for w in guild_webhooks if str(ctx.channel.id) in w.name]
        if not webhooks_filtered:
            webhook: discord.Webhook = await ctx.channel.create_webhook(name=f'say-cmd-hook-{ctx.channel.id}')
        else:
            webhook: discord.Webhook = webhooks_filtered[0]

        await ctx.message.delete()
        await webhook.send(content=content, username=nick, avatar_url=user.avatar_url)


def setup(bot):
    bot.add_cog(Say(bot))
