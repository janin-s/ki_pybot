import random
import re
import datetime
import math
import yfinance

from typing import TypeVar
from discord import Embed
from pytz import timezone
from lib.db import db

from lib.utils.trading_classes import Stock


def get_all_stocks_from_db() -> list[tuple[str, str]]:
    records = db.records('SELECT * FROM assets')
    return records


def create_database_poll_entry(guild_id: int, stock1: Stock, stock2: Stock) -> tuple[int, datetime]:
    berlin = timezone('Europe/Berlin')
    eastern = timezone('US/Eastern')
    start_time: datetime = datetime.datetime.now()
    end_time: datetime = datetime.datetime.now()
    end_time = end_time.replace(hour=9, minute=35)
    # label time as eastern and convert to our timezone to get correct timestamp for our time
    end_time = eastern.localize(end_time).astimezone(berlin)

    new_id = db.field('INSERT INTO trading_polls (guild_id, start_time, end_time, asset1_id, asset2_id) '
                      'VALUES (?,?,?,?,?) RETURNING poll_id',
                      guild_id, start_time.isoformat(), end_time.isoformat(), stock1.id, stock2.id)
    return new_id, end_time


def create_poll_embed(stock: Stock, end_time: datetime) -> Embed:
    embed = Embed(title=stock.symbol)
    embed.add_field(name=stock.shortName, value=stock.description[:1024])
    embed.add_field(name='Current Price', value=f'${stock.currentPrice}')
    embed.add_field(name='Market Cap', value=f'${millify(stock.marketCap)}')
    embed.add_field(name='Current Votes', value='0')
    embed.set_thumbnail(url=stock.logo_url)
    embed.set_footer(text=f'buy time: {end_time.strftime("%H:%M")}')
    return embed


def stock_to_tuple(stock: Stock) -> tuple:
    t = stock.id, stock.symbol, stock.shortName, stock.description, stock.logo_url, stock.currentPrice, stock.marketCap
    return t


def tuple_to_stock(tup: tuple) -> Stock:
    return Stock(*tup)


T = TypeVar('T')


def choose_two(assets: list[T]) -> tuple[T, T] | None:
    if len(assets) < 2:
        return None
    assets = random.sample(assets, k=2)
    return assets[0], assets[1]


def to_stock(stock: tuple[str, str]) -> Stock:
    id, symbol = stock
    ticker = yfinance.Ticker(symbol)
    info = ticker.info
    print(f'\n\n\ninfo: {info}\n\n\n')
    try:
        long_description = info['longBusinessSummary']
        split_description = _split_into_sentences(long_description)
        description = ' '.join(split_description[:2])

        name = info['shortName']
        price = info['regularMarketPrice']
        marketCap = info['marketCap']
        logo_url = info['logo_url']
    except KeyError:
        return Stock(id=id, symbol=symbol, shortName='?', description='?',
                     logo_url='https://upload.wikimedia.org/wikipedia/commons/3/33/White_square_with_question_mark.png',
                     currentPrice=0, marketCap=0)
    return Stock(id=id,
                 symbol=symbol,
                 shortName=name,
                 description=description,
                 logo_url=logo_url,
                 currentPrice=price,
                 marketCap=marketCap)


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()


millnames = ['', 'k', 'M', 'B', 'T']


def millify(n: float | None):
    if n is None:
        return 'N/A'
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return f'{n / 10 ** (3 * millidx):.2f}{millnames[millidx]}'


# from https://stackoverflow.com/a/31505798
def _split_into_sentences(text: str) -> list[str]:
    alphabets = "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"

    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    if "Ph.D" in text:
        text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
    if "”" in text:
        text = text.replace(".”", "”.")
    if "\"" in text:
        text = text.replace(".\"", "\".")
    if "!" in text:
        text = text.replace("!\"", "\"!")
    if "?" in text:
        text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences
