import copy
import functools
import random
import re
import datetime
import math
from pathlib import Path

import discord
import numpy as np
import yfinance
from matplotlib import pyplot as plt

from typing import TypeVar
from alpaca_trade_api.entity import Position, PortfolioHistory
from discord import Embed
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter
from numpy import ndarray

from lib.db import db
from lib.utils.trading_classes import Stock


def update_poll_entry(message_id: int, channel_id: int, poll_id: int) -> None:
    db.execute('UPDATE trading_polls SET message_id = ?, channel_id = ? WHERE poll_id = ?',
               message_id, channel_id, poll_id)


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
    change = float(pos.unrealized_plpc) * 100.

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
    if total_cost == 0:
        return 0.0
    return total_value / total_cost - 1.


def format_portfolio_embeds(cash_string: str, value_string: str, positions: list[Position]) -> list[Embed]:
    value = float(value_string)
    cash = float(cash_string)
    stock_only_val = value - cash
    position_lines: list[str] = _format_positions(positions)
    embed = Embed(title='Portfolio')
    embed.add_field(name='Cash', value=f'${cash:.2f}')
    embed.add_field(name='Portfolio Value', value=f'${stock_only_val:.4f}')
    embed.add_field(name='Total Change', value=f'{_get_total_change(positions) * 100:.4f}%')
    position_embeds = list(map(lambda s: Embed(description=f'```{s}```'), position_lines))
    return [embed] + position_embeds


def get_portfolio_history_image(history: PortfolioHistory) -> discord.File:
    image_path: Path = _build_portfolio_plot_relative(history.timestamp, history.profit_loss)
    return discord.File(fp=image_path, filename='portfolio_history.png')


T = TypeVar('T')


def choose_two(assets: list[T]) -> tuple[T, T] | None:
    if len(assets) < 2:
        return None
    assets = random.sample(assets, k=2)
    return assets[0], assets[1]


async def get_stock_info(symbol: str):
    ticker = yfinance.Ticker(symbol)
    info: dict = ticker.info
    return info


async def to_stock(stock: tuple[str, str]) -> Stock:
    stock_id, symbol = stock
    info = await get_stock_info(symbol)
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


def get_cross_point(x1: float, y1: float, x2: float, y2: float, threshold: float) -> float:
    """returns x coord where line from (x1,y1) to (x2,ys) crosses vertical line at threshold"""
    m = (y2 - y1) / (x2 - x1)
    t = y1 - m * x1
    return (threshold - t) / m


def modify_data(x_orig: list[float], y_orig: list[float], threshold: float) -> tuple[list[float], list[float]]:
    """inserts dummy points at (=slightly above/below) the threshold to make colouring parts of the graph possible"""
    xs = copy.copy(x_orig)
    ys = copy.copy(y_orig)
    xs_zipped = zip(xs[:-1] + [xs[-1]], xs[1:] + [xs[-1]])
    ys_zipped = zip(ys[:-1] + [ys[-1]], ys[1:] + [ys[-1]])
    new_xs = []
    new_ys = []
    for (x1, x2), (y1, y2) in zip(xs_zipped, ys_zipped):
        new_ys.append(y1)
        new_xs.append(x1)

        if y1 < threshold < y2 or y1 >= threshold > y2:
            new_x = get_cross_point(x1, y1, x2, y2, threshold)
            new_xs.append(new_x)
            if y1 < y2:
                new_ys.append(threshold + 0.000000001)
            else:
                new_ys.append(threshold - 0.000000001)
    return new_xs, new_ys


def threshold_plot(
        axs: Axes, xs: ndarray, ys: ndarray, threshv: float, color_below: str, color_above: str
) -> LineCollection:
    # from https://stackoverflow.com/a/30125761
    ys_min, ys_max = np.min(ys), np.max(ys)
    if ys_min <= threshv <= ys_max:
        colors = [color_below, color_above]
        boundaries = [np.min(ys), threshv, np.max(ys)]
    elif threshv < ys_min:
        colors = [color_above]
        boundaries = [np.min(ys), np.max(ys)]
    else:
        colors = [color_below]
        boundaries = [np.min(ys), np.max(ys)]

    cmap = ListedColormap(colors)
    norm = BoundaryNorm(boundaries, cmap.N)

    points = np.array([xs, ys]).T.reshape(-1, 1, 2)
    line_segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = LineCollection(line_segments, cmap=cmap, norm=norm)
    lc.set_array(ys)

    axs.add_collection(lc)
    axs.set_xlim(np.min(xs), np.max(xs))
    ys_min = np.min(ys)
    ys_max = np.max(ys)
    data_range = ys_max - ys_min
    axs.set_ylim(ys_min - 0.1 * data_range, ys_max + 0.1 * data_range)
    return lc


def _accumulate_changes(profit_loss: list[float]) -> list[float]:
    current_sum = 0
    for idx, val in enumerate(profit_loss):
        current_sum = current_sum + val
        profit_loss[idx] = current_sum
    return profit_loss


def get_axis_marker_interval(plot_start: int, plot_end: int) -> int:
    start_date = datetime.date.fromtimestamp(plot_start)
    end_date = datetime.date.fromtimestamp(plot_end)
    weeks = (end_date - start_date).days / 7
    interval = math.ceil(weeks / 16)  # 16 markers nicely fit on the image
    return interval


def _build_portfolio_plot_relative(timestamps_unix: list[int], profit_loss: list[float]) -> Path:
    THRESHOLD = 0.
    fig: Figure
    ax: Axes
    style_path = Path('styles/portfolio.mplstyle')
    plt.style.use(style_path.absolute())

    fig, ax = plt.subplots()

    # styles and formatting
    interval = get_axis_marker_interval(plot_start=timestamps_unix[0], plot_end=timestamps_unix[-1])
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=interval))
    fig.autofmt_xdate()

    # prepare data
    profit_loss = _accumulate_changes(profit_loss)
    timestamps = [t / 86400 for t in timestamps_unix]
    timestamps_mod, values_mod = modify_data(x_orig=timestamps, y_orig=profit_loss, threshold=THRESHOLD)
    timestamps_modified = np.asarray(timestamps_mod)
    values_modified = np.asarray(values_mod)

    # get line colored according to threshold
    lc = threshold_plot(ax, np.asarray(timestamps_modified), np.asarray(values_modified), THRESHOLD, 'darkred', 'green')
    lc.set_linewidth(2)

    # add horizontal line
    ax.axhline(THRESHOLD, color='#ada4a4')

    # file area between curve and horizontal line
    ax.fill_between(
        timestamps_modified, values_modified, THRESHOLD, where=(values_modified < THRESHOLD), facecolor="red", interpolate=True
    )
    ax.fill_between(
        timestamps_modified, values_modified, THRESHOLD, where=(values_modified > THRESHOLD), facecolor="limegreen", interpolate=True
    )

    figure_path = Path('data/other/portfolio.png')
    plt.savefig(figure_path.absolute())
    return figure_path


def seconds_until(hours: int, minutes: int) -> float:
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()


millnames = ['', 'k', 'M', 'B', 'T']


def millify(n: float | None) -> str:
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
