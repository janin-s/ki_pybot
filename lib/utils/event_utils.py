from datetime import datetime

from discord import Embed

from lib.utils.event_classes import Event


def parse_command_args(arg: str) -> tuple[str, str, str, datetime, datetime, str]:
    args = arg.split(';')
    if len(args) != 7:
        raise ValueError('Invalid number of arguments')
    name: str = args[0]
    description: str = args[1]
    place = args[6]
    try:
        start = datetime.strptime(args[2] + ';' + args[3], '%Y-%m-%d;%H:%M')
        end = datetime.strptime(args[4] + ';' + args[5], '%Y-%m-%d;%H:%M')
    except ValueError:
        raise ValueError("Couldn't parse date")
    role_name = f'event-{"-".join(name.lower().split(" "))}'
    return name, description, place, start, end, role_name


def create_event_embed(name: str, description: str, place: str, start: datetime, end: datetime) -> Embed:
    embed = Embed(title=name, description=description)
    embed.add_field(name='When?', value=f'{start.strftime("%H:%M %d.%m.%y")} - {end.strftime("%H:%M %d.%m.%y")}')
    embed.add_field(name='Where?', value=place)
    return embed


def tuple_to_event(t: tuple) -> Event:
    return Event(*t[1:])
