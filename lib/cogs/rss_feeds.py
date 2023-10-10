import dataclasses
import itertools
import textwrap
from collections.abc import Iterable
from datetime import datetime, timedelta
from time import mktime
from typing import Literal

import discord
import feedparser
from discord import Embed
from discord.ext import commands, tasks
from discord.ext.commands import Cog, command, Context
from feedparser import FeedParserDict
from markdownify import markdownify as md
from bs4 import BeautifulSoup

from lib.db import db
from lib.bot import Bot

FeedId = Literal['fefe', 'schneier', 'jbl', 'kuketz', 'xkcd']


@dataclasses.dataclass(frozen=True)
class FeedEntry:
    title: str
    summary: str | None
    link: str | None
    published: datetime | None
    id: str | None
    image: str | None = None


@dataclasses.dataclass(frozen=True)
class RSSFeed:
    id: FeedId
    title: str
    link: str
    icon_url: str
    updated: datetime | None
    entries: list[FeedEntry]


@dataclasses.dataclass(frozen=True)
class Image:
    url: str
    title: str | None


FEED_COLOURS: dict[FeedId, int] = {
    'fefe': 0xFFFFFF,
    'schneier': 0x6b0000,
    'jbl': 0x000000,
    'kuketz': 0x628098,
    'xkcd': 0x96A8C8,
}

FEEDS: list[tuple[FeedId, str]] = [
    ('fefe', 'https://blog.fefe.de/rss.xml?html'),
    ('schneier', 'https://www.schneier.com/feed/'),
    ('jbl', 'https://blog.cr.yp.to/feed.application=xml'),
    ('kuketz', 'https://www.kuketz-blog.de/feed/'),
    ('xkcd', 'https://xkcd.com/rss.xml'),
]

UPDATE_MINUTES = 10

FEED_CHANNEL_ID = 1160283395717349406


def extract_images(content: str) -> Image | None:
    soup = BeautifulSoup(content, features='html.parser')
    img = soup.find('img')
    if not img:
        return None
    return Image(
        url=img['src'],
        title=img.get('title')
    )


def extract_data(feed_id: FeedId, result: FeedParserDict) -> RSSFeed:
    updated_time = datetime.fromtimestamp(mktime(result.updated_parsed)) if 'updated_parsed' in result else None
    icon_url = (result.feed.image.href
                if 'image' in result.feed
                else f'https://www.google.com/s2/favicons?domain_url={result.feed.link}')
    feed = RSSFeed(
        id=feed_id,
        title=result.feed.title,
        updated=updated_time,
        entries=[],
        link=result.feed.link,
        icon_url=icon_url
    )
    for e in result.entries:
        image = extract_images(e.summary)
        content = md(e.summary, strip=['img']) if 'summary' in e else None
        if not content:
            if image:
                content = image.title
            else:
                continue
        published_time = datetime.fromtimestamp(mktime(e.published_parsed)) if 'published_parsed' in e else None
        feed.entries.append(
            FeedEntry(
                title=e.title,
                summary=content,
                link=e.link if 'link' in e else None,
                published=published_time,
                id=e.id if 'id' in e else None,
                image=image.url if image else None
            )
        )
    return feed


def format_entry(feed: RSSFeed, entry: FeedEntry) -> Embed:
    embed = discord.Embed(title=entry.title,
                          url=entry.link,
                          description=entry.summary,
                          colour=FEED_COLOURS.get(feed.id, 0x57F287),
                          timestamp=entry.published if entry.published else None)

    embed.set_author(name=feed.title,
                     url=feed.link,
                     icon_url=feed.icon_url
                     )

    embed.set_footer(text=feed.title)

    if entry.image:
        embed.set_image(url=entry.image)
    return embed


def get_db_key(entry: FeedEntry) -> str:
    return textwrap.dedent(
        f'''\
        {entry.id if entry.id else ""}_
        {entry.published if entry.published else ""}_
        {entry.link if entry.link else ""}'''
    ).replace('\n', '')


class RSS(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        records = db.records('SELECT feed_id, last_entry_id FROM rss_feed_last_entries')
        self.last_entries = {feed_id: last_entry_id for feed_id, last_entry_id in records}

        self.rss_update_loop.start()

    @command()
    @commands.has_permissions(administrator=True)
    async def get_feeds(self, ctx: Context):
        await self.rss_update_loop(channel_id=ctx.channel.id)

    def get_new_entries(self, feed: RSSFeed) -> Iterable[FeedEntry]:
        if feed.updated and feed.updated > (datetime.now() - timedelta(minutes=UPDATE_MINUTES)):
            return []

        def entry_is_new(entry: FeedEntry) -> bool:
            if entry.published and entry.published > (datetime.now() - timedelta(minutes=UPDATE_MINUTES)):
                return True
            key = get_db_key(entry)
            res = key != self.last_entries.get(feed.id)
            return res

        return reversed(list(itertools.takewhile(entry_is_new, feed.entries)))

    @tasks.loop(minutes=UPDATE_MINUTES)
    async def rss_update_loop(self, channel_id=FEED_CHANNEL_ID):
        channel = await self.bot.fetch_channel(channel_id)
        for feed_id, feed_url in FEEDS:
            res = feedparser.parse(feed_url)
            feed = extract_data(feed_id, res)
            new_entries = self.get_new_entries(feed)

            for entry in new_entries:
                embed = format_entry(feed, entry)
                self.last_entries[feed.id] = get_db_key(entry)
                await channel.send(embed=embed)
        await self.safe_newest_entry()

    async def safe_newest_entry(self):
        for feed_id, last_entry_id in self.last_entries.items():
            db.execute('REPLACE INTO rss_feed_last_entries (feed_id, last_entry_id) VALUES (?, ?)',
                       feed_id, last_entry_id)

    @rss_update_loop.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("rss_feeds")

    def cog_unload(self):
        self.rss_update_loop.cancel()


def setup(bot):
    bot.add_cog(RSS(bot))
