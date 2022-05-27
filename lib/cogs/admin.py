from apscheduler.job import Job
from discord.ext.commands import Cog, command
from discord.ext import commands

from lib.bot import COGS, Bot
from lib.db import db


class Admin(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("admin")

    @command(name='load')
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, cog):
        """Loads a previously not loaded Cog"""
        if cog not in COGS:
            await ctx.send(f'cog \"{cog}\" not found')
            return

        self.bot.load_extension(f"lib.cogs.{cog}")
        await ctx.message.add_reaction('\U00002705')

    @command(name='unload')
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, cog):
        """Unloads a previously loaded Cog"""
        if cog not in COGS or cog == "admin":
            await ctx.send(f'cog \"{cog}\" not found or invalid')
            return

        self.bot.unload_extension(f"lib.cogs.{cog}")
        await ctx.message.add_reaction('\U00002705')

    @command(name='reload')
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, cog):
        """Reloads a previously loaded Cog"""
        if cog not in COGS:
            await ctx.send(f'cog \"{cog}\" not found')
            return
        self.bot.reload_extension(f"lib.cogs.{cog}")
        await ctx.message.add_reaction('\U00002705')

    @command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount=1):
        """Löscht die übergebene Anzahl an Messages (default == 1) mit !clear {amount}*"""
        quote_channel = db.execute('SELECT quote_channel FROM server_info WHERE guild_id = ?', ctx.guild.id)
        if ctx.channel.id == quote_channel:
            await ctx.message.delete
            await ctx.send('Pseudohistorie wird hier nicht geduldet!', delete_after=60)
            return
        purge_limit = min(amount + 1, 200)
        await ctx.channel.purge(limit=purge_limit)

    @command()
    @commands.has_permissions(administrator=True)
    async def get_jobs(self, ctx):
        def show_job(job: Job) -> str:
            return f'Job ({job.id=} {job.name=} {job.func=} {job.args=} {job.next_run_time=}'
        result = ', '.join(map(show_job, self.bot.scheduler.get_jobs()))

        await ctx.send(result)


def setup(bot):
    bot.add_cog(Admin(bot))
