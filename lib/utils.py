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
        return datetime.today()
    if s == 'morgen' or s == 'tomorrow':
        return datetime.today() + timedelta(days=1)
    if ';' in s:
        time = ';%H:%M'
    else:
        time = ''
    if s.count('.') == 2:
        year = ".%Y"
    else:
        year = ''
    parsed = datetime.strptime(s, f'%d.%m{year}{time}')
    if year == '':
        parsed = parsed.replace(year=datetime.now().year)
    return parsed
