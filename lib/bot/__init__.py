from asyncio import sleep

from discord.ext.commands import Bot as BotBase
from discord.ext import commands
from discord import Intents, File
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # idk
from glob import glob

PREFIX = "!"
OWNER_ID = 388061626131283968
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]  # wtf


class Ready(object):
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
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        super().__init__(
            command_prefix=PREFIX,
            owner_id=OWNER_ID,
            intents=Intents.all(),
            case_insensitive=True
        )

    # loading cogs
    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("setup complete")

    def run(self, version):
        self.VERSION = version

        self.setup()

        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("bot running")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("iwas falsch oh no :(")
            print("help :(")

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.errors.CommandNotFound):
            await ctx.send('KI dummdumm <:eist_moment:731293248324370483>')
        elif isinstance(exc, commands.errors.CommandOnCooldown):
            await ctx.send("nicht so schnell")
        elif isinstance(exc, commands.errors.BotMissingPermissions):
            await ctx.send("KI nicht mächtig genug :(")
        else:
            await ctx.send("KI nix verstehi ._." + str(exc))

    async def on_ready(self, version):
        if not self.ready:
            self.guild = self.get_guild(705425948996272210)

            #wait for cogs to be ready
            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("bot ready")
        else:
            print("bot reconnected")

    async def on_message(self, message):
        pass


bot = Bot()
