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


def parse_date(birthdate: str) -> [int, int]:
    if birthdate == "today":
        return [datetime.today().day, datetime.today().month]

    if birthdate == "tomorrow":
        tmrw = datetime.today() + timedelta(days=1)
        return [tmrw.day, tmrw.month]

    try:
        # date = parser.parse(birthdate, dayfirst=True, yearfirst=False, fuzzy=True)
        date = parse_datestr(birthdate)
    except ValueError:
        return 0, 0

    return [date.day, date.month]


def parse_reminder(s: str) -> datetime:
    if s == 'morgen':
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


def parse_datestr(s: str) -> datetime:
    splitted = s.split('.')
    if len(splitted) < 2:
        raise ValueError
    yr = datetime.today().year
    if len(splitted) >= 3:
        yr = splitted[3]
    return datetime(year=yr, month=int(splitted[1]), day=int(splitted[0]))
