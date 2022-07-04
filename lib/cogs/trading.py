import asyncio
import discord
import alpaca_trade_api

from datetime import datetime, timedelta
from alpaca_trade_api.common import URL
from alpaca_trade_api.entity import Asset, Order, Clock, Account, Position, PortfolioHistory
from apscheduler.triggers.date import DateTrigger
from discord import Message, HTTPException
from discord.ext import tasks
from discord.ext.commands import Cog, has_permissions, command, Context
from pytz import timezone

from lib.bot import Bot
from lib.db import db
from lib.utils.trading_classes import StockError, StockButton, count_votes
from lib.utils.trading_utils import Stock, choose_two, to_stock, seconds_until, create_poll_embed, \
    create_database_poll_entry, get_all_stocks_from_db, format_portfolio_embeds, add_buytime_noise, \
    get_portfolio_history_image, update_poll_entry
from lib.utils.utils import Channel


class Trading(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        api_key_id = self.bot.config.alpaca_api_key_id
        api_secret = self.bot.config.alpaca_api_secret
        api_endpoint = URL('https://api.alpaca.markets')
        paper_api_key_id = 'PKZ0AFHB21M8WVI8UMX3'
        paper_api_secret_key = 'AXBHvjLKqMQPQDEwosddasP0CZqjAUuvV6trCy3x'
        paper_endpoint = URL('https://paper-api.alpaca.markets')
        self.api = alpaca_trade_api.REST(key_id=api_key_id,
                                         secret_key=api_secret,
                                         base_url=api_endpoint)
        self.pinned_messages: list[Message] = []
        self.create_poll_loop.start()

    @Cog.listener()
    async def on_ready(self):
        records = db.records(
            'SELECT poll_id, guild_id, asset1_id, asset2_id, message_id, channel_id FROM trading_polls '
            'WHERE end_time > ?',
            datetime.now().isoformat())
        for poll_id, guild_id, asset1_id, asset2_id, message_id, channel_id in records:
            await self.update_trading_view(asset1_id, asset2_id, channel_id, guild_id, message_id, poll_id)

        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("trading")

    async def update_trading_view(self, asset1_id: str, asset2_id: str, channel_id: int, guild_id: int, message_id: int,
                                  poll_id: int) -> None:
        guild = await self.bot.fetch_guild(guild_id)
        channel = await guild.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        symbol1 = db.field('SELECT symbol FROM assets WHERE id = ?', asset1_id)
        symbol2 = db.field('SELECT symbol FROM assets WHERE id = ?', asset2_id)
        if symbol1 and symbol2 and message:
            view = discord.ui.View(timeout=None)
            view.add_item(StockButton(symbol1, asset1_id, poll_id))
            view.add_item(StockButton(symbol2, asset2_id, poll_id))
            await message.edit(view=view)
            self.bot.add_view(view, message_id=message_id)

    @command()
    async def portfolio_history(self, ctx: Context):
        history: PortfolioHistory = self.api.get_portfolio_history(date_start='2022-05-28', timeframe='1D')
        file: discord.File = get_portfolio_history_image(history)
        await ctx.send(file=file)

    @command()
    async def portfolio(self, ctx: Context):
        account, positions = self._get_account_and_positions()
        cash: str = account.cash
        portfolio_value: str = account.equity
        embeds = format_portfolio_embeds(cash, portfolio_value, positions)
        await ctx.send(embeds=embeds)

    def _get_account_and_positions(self) -> tuple[Account, list[Position]]:
        positions: list[Position] = self.api.list_positions()
        account: Account = self.api.get_account()
        return account, positions

    def _get_next_buy_time(self) -> datetime:
        berlin = timezone('Europe/Berlin')
        market_clock: Clock = self.api.get_clock()
        next_open_iso: str = market_clock._raw['next_open']
        eastern_time = datetime.fromisoformat(next_open_iso) + timedelta(minutes=30)
        berlin_time = eastern_time.astimezone(berlin)
        return berlin_time
        # return (datetime.now() + timedelta(minutes=2)).replace(second=0, microsecond=0)

    def _update_stocks(self) -> None:
        all_assets: list[Asset] = self.api.list_assets(status='active', asset_class='us_equity')
        relevant_assets = list(filter(lambda a: a.fractionable and a.tradable and a.status == 'active', all_assets))
        insert_statement = 'INSERT INTO assets (id, symbol) VALUES (?, ?)'

        db.execute('DELETE FROM assets')
        db.multiexec(insert_statement, map(lambda a: (a.id, a.symbol), relevant_assets))

    def _buy_stock(self, stock: Stock):
        response: Order = self.api.submit_order(symbol=stock.symbol,
                                                notional=1.,
                                                side='buy',
                                                type='market',
                                                time_in_force='day',
                                                order_class='simple')
        print(response)
        if response.status in ['canceled', 'stopped', 'rejected', 'suspended']:
            raise StockError('Order not accepted')

    @tasks.loop(hours=24)
    async def create_poll_loop(self):
        await asyncio.sleep(seconds_until(9, 0))
        records = db.records('SELECT guild_id, trading_channel FROM server_info')
        for guild_id, trading_channel in records:
            channel = await self.bot.fetch_channel(trading_channel)
            await self._create_poll(channel, guild_id)

    @command()
    @has_permissions(administrator=True)
    async def create_poll(self, ctx: Context):
        await self._create_poll(ctx.channel, ctx.guild.id)

    async def _create_poll(self, channel: Channel, guild_id: int):
        stocks = get_all_stocks_from_db()
        chosen_stocks = choose_two(stocks)
        if not chosen_stocks:
            self._update_stocks()
            stocks = get_all_stocks_from_db()
            chosen_stocks = choose_two(stocks)
            if not chosen_stocks:
                await channel.send('No Stocks found :(')
                return

        stock1 = await to_stock(chosen_stocks[0])
        stock2 = await to_stock(chosen_stocks[1])

        buy_time = self._get_next_buy_time()
        poll_id = create_database_poll_entry(guild_id, stock1, stock2, buy_time)

        embed1 = create_poll_embed(stock1, buy_time)
        embed2 = create_poll_embed(stock2, buy_time)

        view = discord.ui.View(timeout=None)
        view.add_item(StockButton(stock1.symbol, stock1.id, poll_id))
        view.add_item(StockButton(stock2.symbol, stock2.id, poll_id))

        job_buy_time = add_buytime_noise(buy_time, poll_id)
        # add job for evaluation
        self.bot.scheduler.add_job(
            name=f'Poll {poll_id}',
            func=self._evaluate_poll,
            trigger=DateTrigger(job_buy_time),
            args=[poll_id, channel],
            misfire_grace_time=None)
        short_message: Message = await channel.send(content=f'Poll for {stock1.symbol} & {stock2.symbol}')
        embed_message: Message = await channel.send(embeds=[embed1, embed2], view=view)
        update_poll_entry(embed_message.id, embed_message.channel.id, poll_id)

        self.pinned_messages.append(short_message)
        try:
            await short_message.pin()
        except HTTPException:
            pass

    async def _evaluate_poll(self, poll_id: int, channel: Channel):
        print(f'Evaluating poll {poll_id}')
        poll_record = db.record('SELECT start_time, end_time, asset1_id, asset2_id FROM trading_polls WHERE poll_id =?',
                                poll_id)
        if poll_record is None:
            await channel.send(f'Couldn\'t find poll with id {poll_id}')
            return
        start_time, end_time, asset1_id, asset2_id = poll_record

        count1 = count_votes(poll_id, asset1_id)
        count2 = count_votes(poll_id, asset2_id)
        if count1 > count2:
            winner = asset1_id
        else:
            winner = asset2_id
        winner_symbol = db.field('SELECT symbol FROM assets WHERE id = ?', winner)
        winner_stock = await to_stock((winner, winner_symbol))

        try:
            self._buy_stock(winner_stock)
        except StockError:
            await channel.send(f'Order for Stock Voting Winner **${winner_symbol}** not accepted :(')
            return
        await channel.send(f'Submitted buy order for $1 of Stock Voting Winner **${winner_symbol}** at current price '
                           f'${winner_stock.currentPrice}')
        if self.pinned_messages:
            message = self.pinned_messages.pop(0)
            await message.unpin()


def setup(bot):
    bot.add_cog(Trading(bot))
