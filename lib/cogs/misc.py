import os.path
import random

import tweepy as tw
from discord import Member
from discord.ext.commands import Cog, command

from lib.bot import Bot
from lib.db import db


class Misc(Cog):
    api_key = ''
    api_secret = ''
    bearer_token = ''
    api = None
    tweets: [tw.Tweet] = None

    def __init__(self, bot):
        # setup folder for
        if not os.path.exists('./data/other'):
            os.mkdir('./data/other')

        self.api_key = bot.config.twitter_api_key
        self.api_secret = bot.config.twitter_api_secret
        self.bearer_token = bot.config.twitter_bearer_token

        self.client = tw.Client(bearer_token=self.bearer_token,
                                consumer_key=self.api_key,
                                consumer_secret=self.api_secret,
                                wait_on_rate_limit=True,
                                return_type=tw.Response)

        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")

    good_nicks = ['beliebter big brain B Baum bauer', 'lieber chrisl', 'gros gehirn chrisl']

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        if before.id == 174900012340215809 and after.nick not in self.good_nicks:
            good_nick = random.choice(self.good_nicks)
            await after.edit(nick=good_nick)

    @command()
    async def amongus(self, ctx):
        """switches channel limit for current voice channel from infinity to 99 and back"""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
        else:
            await ctx.send("not connected to a voice channel!")
            return
        current_limit = channel.user_limit
        if current_limit == 0:
            await channel.edit(user_limit=99)
            await ctx.send("among us modus (user anzahl sichtbar) aktiviert")
        else:
            await channel.edit(user_limit=0)
            await ctx.send("among us modus (user anzahl sichtbar) deaktiviert")

    @command()
    async def zitat(self, ctx, length=1):
        """!zitat [x]; zitiert die letze[n x] Nachricht[en] und speichert sie in Relikte"""
        zitat: str = ""
        message_list = []
        async for message in ctx.channel.history(limit=length + 1):
            message_list.append(message)
        message_list.reverse()
        for msg in message_list:
            zitat += msg.author.display_name + ": \"" + msg.content + "\"\n"
        quote_channel_id = db.field("SELECT quote_channel FROM server_info WHERE guild_id = ?", ctx.guild)
        if quote_channel_id is None:
            quote_channel_id = ctx.channel.id
        quote_channel = await self.bot.fetch_channel(quote_channel_id)
        await quote_channel.send(zitat)

    @command(aliases=['mülltake', 'shittake'])
    async def trashtake(self, ctx):
        """based take on the current political situation"""
        user_id = 809188392089092097
        # if list empty get new tweets
        if self.tweets is None or len(self.tweets) == 0:
            response: tw.Response = self.client.get_users_tweets(id=user_id,
                                                                 exclude=['replies', 'retweets'],
                                                                 max_results=100)
            self.tweets = response.data

        # get first tweet in list
        tweet: tw.Tweet = self.tweets.pop(0)
        await ctx.send(tweet.text)


def setup(bot):
    bot.add_cog(Misc(bot))
