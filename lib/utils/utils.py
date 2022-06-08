from datetime import datetime, timedelta

import discord.utils
import requests
from discord import Thread
from discord.abc import GuildChannel, PrivateChannel

Channel = GuildChannel | PrivateChannel | Thread


async def send_paginated(ctx, limit=2000, start="", end="", *, content):
    content = discord.utils.escape_mentions(content)
    content = content.replace('`', '`\u200b')
    if len(content) + len(start) + len(end) < limit:
        await ctx.send(start + content + end)
        return
    chunk_size = limit - len(start) - len(end)
    chunks = [start + content[i:i + chunk_size] + end for i in range(0, len(content), chunk_size)]
    for chunk in chunks:
        await ctx.send(chunk)


def parse_datetime(s: str) -> datetime:
    """parses a string to a datetime object"""
    # date: DD.MM[.YYYY]|morgen|tomorrow
    # time: HH:MM
    # valid strings: date;time | date | time
    day = datetime.now().day
    if s.startswith('morgen') or s.startswith('tomorrow'):
        day = (datetime.today() + timedelta(days=1)).day
        s = s.removeprefix('morgen').removeprefix('tomorrow')

    dots = s.count('.')
    if dots == 2:
        date = '%d.%m.%Y'
    elif dots == 1:
        date = '%d.%m'
    else:
        date = ''

    if ';' in s:
        time = ';%H:%M'
    elif dots == 0:
        time = '%H:%M'
    else:
        time = ''
    parsed = datetime.strptime(s, f'{date}{time}')
    # if no year was specified set it to the current year
    now = datetime.now()
    if dots == 0:
        parsed = parsed.replace(year=now.year, month=now.month, day=day)
    elif dots == 1:
        parsed = parsed.replace(year=now.year)
    return parsed


def true_random_int(lower: int, upper: int, amount: int = 1):
    req = f'https://www.random.org/integers/?num={amount}&min={lower}&max={upper}&col=1&base=10&format=plain&rnd=new'
    num_string = requests.get(req).text
    try:
        ints = [int(s) for s in num_string.split('\n')[:-1]]
    except ValueError:
        print(f"error when parsing results of random.org call, result: {num_string}")
        return []
    return ints
