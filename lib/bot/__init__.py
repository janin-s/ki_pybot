import os
import sys
from asyncio import sleep

from discord.ext.commands import Bot as BotBase
from discord.ext import commands
from discord import Intents, utils, Forbidden
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from lib.bot.config import Config
from lib.db import db
from lib.cogs import msg
from lib.utils import MsgNotFound

COGS = [path[:-3] for path in os.listdir('./lib/cogs') if path[-3:] == '.py']


class Ready():
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        config_file = "config.toml"
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
        self.config = Config(config_file)
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=self.config.command_prefix,
            owner_id=self.config.owner_id,
            intents=Intents.all(),
            description=self.config.desc,
            case_insensitive=True
        )

    # loading cogs
    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("setup complete")

    def run(self):
        self.setup()

        print("running bot..")
        super().run(self.config.discord_token, reconnect=True)

    async def on_connect(self):
        print("bot running")

    async def on_disconnect(self):
        print("bot disconnected")

#   async def on_error(self, err, *args, **kwargs):
#     if err == "on_command_error":
#            await args[0].send("iwas falsch oh no :(")
#            print("help :(")

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.errors.CommandNotFound):
            try:
                await msg.message(ctx=ctx, msg=ctx.invoked_with)
            except MsgNotFound:
                await ctx.send('KI dummdumm v2 <:eist_moment:731293248324370483>')

        elif isinstance(exc, commands.errors.CommandOnCooldown):
            await ctx.send("nicht so schnell")
        elif isinstance(exc, commands.errors.BotMissingPermissions):
            await ctx.send("KI nicht mächtig genug :(")
        else:
            await ctx.send("KI nix verstehi ._." + str(exc))

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(self.config.guild_id)
            self.scheduler.start()
            # wait for cogs to be ready
            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("bot ready")
        else:
            print("bot reconnected")

    async def on_member_join(self, member):
        user_id = member.id
        guild_id = member.guild.id
        nick = db.field('SELECT display_name FROM users WHERE id = ? AND guild_id = ?',
                        user_id, guild_id)
        if nick is not None:
            await member.edit(nick=nick)
        roles = db.column('SELECT role_id FROM roles WHERE user_id = ? AND guild_id = ?',
                          user_id, guild_id)
        if roles is not None:
            for role_id in roles:
                role = utils.get(member.guild.roles, id=role_id)
                if role.name != "@everyone":
                    try:
                        await member.add_roles(role)
                    except Forbidden:
                        print(f'not able to add role with id {role_id}')


bot = Bot()
