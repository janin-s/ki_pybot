import functools
import random
import re
import datetime
import math

import numpy as np
import yfinance
from matplotlib import pyplot as plt

from typing import TypeVar
from alpaca_trade_api.entity import Position, PortfolioHistory
from discord import Embed
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.dates as mdates
from numpy import ndarray

from lib.db import db
from lib.utils.trading_classes import Stock


def add_buytime_noise(buy_time: datetime.datetime, poll_id: int) -> datetime.datetime:
    return buy_time + datetime.timedelta(seconds=poll_id % 60, milliseconds=random.randint(0, 99))


def get_all_stocks_from_db() -> list[tuple[str, str]]:
    records = db.records('SELECT * FROM assets')
    return records


def create_database_poll_entry(guild_id: int, stock1: Stock, stock2: Stock, buy_time: datetime.datetime) -> int:
    start_time: datetime = datetime.datetime.now()

    new_id = db.field('INSERT INTO trading_polls (guild_id, start_time, end_time, asset1_id, asset2_id) '
                      'VALUES (?,?,?,?,?) RETURNING poll_id',
                      guild_id, start_time.isoformat(), buy_time.isoformat(), stock1.id, stock2.id)
    return new_id


def create_poll_embed(stock: Stock, end_time: datetime) -> Embed:
    embed = Embed(title=stock.symbol)
    embed.add_field(name=stock.shortName, value=stock.description[:1024])
    embed.add_field(name='Current Price', value=f'${stock.currentPrice}')
    embed.add_field(name='Market Cap', value=f'${millify(stock.marketCap)}')
    embed.add_field(name='Current Votes', value='0')
    embed.set_thumbnail(url=stock.logo_url)
    embed.set_footer(text=f'buy time: {end_time.strftime("%H:%M")}')
    return embed


def _position_to_str(pos: Position) -> str:
    cost_basis = float(pos.cost_basis)
    market_value = float(pos.market_value)
    change = float(pos.unrealized_plpc)

    def pad(s: str, length: int) -> str:
        return s + (length - len(s)) * ' '

    return f" {pad(pos.symbol, 8)} " \
           f"${pad(f'{cost_basis:.2f}', 9)} " \
           f"${pad(f'{market_value:.4f}', 12)} " \
           f"{pad(f'{change:.3f}%', 8)}"


def _format_positions(positions: list[Position]) -> list[str]:
    position_strs: list[str] = list(map(_position_to_str, positions))
    header = 'Symbol | BuyPrice | MarketValue | rel. Change'
    all_lines = [header] + position_strs
    return ['\n'.join(all_lines[i:i + 94]) for i in range(0, len(all_lines), 94)]


def _get_total_change(positions: list[Position]) -> float:
    total_cost, total_value = functools.reduce(lambda t1, t2: (t1[0] + t2[0], t1[1] + t2[1]),
                                               map(lambda p: (float(p.cost_basis), float(p.market_value)), positions),
                                               (0, 0))
    print(f'{total_cost=}, {total_value=}')
    return total_value / total_cost - 1.


def format_portfolio_embeds(cash_string: str, value_string: str, positions: list[Position]) -> list[Embed]:
    value = float(value_string)
    cash = float(cash_string)
    stock_only_val = value - cash
    position_lines: list[str] = _format_positions(positions)
    embed = Embed(title='Portfolio')
    embed.add_field(name='Cash', value=f'${cash:.2f}')
    embed.add_field(name='Portfolio Value', value=f'${stock_only_val:.4f}')
    embed.add_field(name='Total Change', value=f'{_get_total_change(positions):.4f}%')
    position_embeds = list(map(lambda s: Embed(description=f'```{s}```'), position_lines))
    return [embed] + position_embeds


def format_portfolio_history(history: PortfolioHistory):
    print(history._raw)
    _build_portfolio_plot(history.timestamp, history.equity, history.profit_loss_pct)

T = TypeVar('T')


def choose_two(assets: list[T]) -> tuple[T, T] | None:
    if len(assets) < 2:
        return None
    assets = random.sample(assets, k=2)
    return assets[0], assets[1]


def to_stock(stock: tuple[str, str]) -> Stock:
    stock_id, symbol = stock
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
        return Stock(id=stock_id, symbol=symbol, shortName='?', description='?',
                     logo_url='https://upload.wikimedia.org/wikipedia/commons/3/33/White_square_with_question_mark.png',
                     currentPrice=0, marketCap=0)
    return Stock(id=stock_id,
                 symbol=symbol,
                 shortName=name,
                 description=description,
                 logo_url=logo_url,
                 currentPrice=price,
                 marketCap=marketCap)


def _build_portfolio_plot(timestamp: list[int], equity: list[float], profit_loss_pct: list[float]):
    BOUNDARY = 100_000
    equity = [e if e > 0.000001 else BOUNDARY for e in equity]

    dates = list(map(lambda t: datetime.datetime.fromtimestamp(t).strftime('%d.%m'), timestamp))

    print(f'{dates=}, {equity=}')
    plt.plot(dates, equity)
    plt.axhline(y=BOUNDARY, xmin=0, xmax=1, color='b', linestyle=':')
    plt.show()

    #c = ['r' if e < 100000 else 'g' for e in equity]
    #cmap = ListedColormap(['r', 'g'])
    #norm = BoundaryNorm([0, BOUNDARY], cmap.N, extend='max')
    #points = np.array([x, y]).T.reshape(-1, 1, 2)
    #segments = np.concatenate([points[:-1], points[1:]], axis=1)
#
    #fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
#
    #lc = LineCollection(segments, cmap=cmap, norm=norm)
    ## lc.set_array(dydx)
    #lc.set_linewidth(2)
    #line = axs[1].add_collection(lc)
    #fig.colorbar(line, ax=axs[1])
    #plt.xlim(x.min(), x.max())
    #plt.ylim(y.min(), y.max())


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
