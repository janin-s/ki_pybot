from discord.ext.commands import Cog, command
from discord.ext import commands

from lib.bot import AVAILABLE_COGS, COGS
from lib.db import db


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('admin')

    @command(name='load')
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, cog):
        """Loads a previously not loaded Cog"""
        if cog not in AVAILABLE_COGS:
            await ctx.send(f'cog \"{cog}\" not found')
            return
        if cog not in COGS:
            COGS.append(cog)
        self.bot.load_extension(f'lib.cogs.{cog}')
        await ctx.message.add_reaction('\U00002705')

    @command(name='unload')
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, cog):
        """Unloads a previously loaded Cog"""
        if cog not in COGS or cog == 'admin':
            await ctx.send(f'cog \"{cog}\" not found or invalid')
            return
        COGS.remove(cog)
        self.bot.unload_extension(f'lib.cogs.{cog}')
        await ctx.message.add_reaction('\U00002705')

    @command(name='reload')
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, cog):
        """Reloads a previously loaded Cog"""
        if cog not in COGS:
            await ctx.send(f'cog \"{cog}\" not found')
            return
        self.bot.reload_extension(f'lib.cogs.{cog}')
        await ctx.message.add_reaction('\U00002705')

    @command(name='get_cogs')
    @commands.has_permissions(administrator=True)
    async def get_cogs(self, ctx):
        """prints which Cogs are loaded or available"""
        s = 'Loaded Cogs: ' + ", ".join(COGS)
        s += '\nAdditionally available Cogs: ' + ', '.join([cog for cog in AVAILABLE_COGS if cog not in COGS])
        await ctx.send(s)



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


def setup(bot):
    bot.add_cog(Admin(bot))
