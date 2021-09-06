from datetime import datetime, timedelta
from dateutil import parser


class MsgNotFound(Exception):
    pass


async def send_paginated(ctx, limit=2000, start="", end="", *, content):
    if len(content) + len(start) + len(end) < limit:
        await ctx.send(start + content + end)
        return
    chunk_size = limit - len(start) - len(end)
    chunks = [start + content[i:i + chunk_size] + end for i in range(0, len(content), chunk_size)]
    for chunk in chunks:
        await ctx.send(chunk)


def parse_datetime(s: str) -> datetime:
    if s == 'heute' or s == 'today':
        return datetime.today().replace(hour=0, minute=0)
    if s == 'morgen' or s == 'tomorrow':
        return datetime.today().replace(hour=0, minute=0) + timedelta(days=1)
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
        parsed = parsed.replace(year=now.year, month=now.month, day=now.day)
    elif dots == 1:
        parsed = parsed.replace(year=now.year)
    return parsed
