import asyncio
import discord
import alpaca_trade_api

from datetime import datetime, timedelta
from alpaca_trade_api.common import URL
from alpaca_trade_api.entity import Asset, Order
from apscheduler.triggers.date import DateTrigger
from discord import TextChannel, Message
from discord.ext import tasks
from discord.ext.commands import Cog, has_permissions, command, Context
from lib.db import db
from lib.utils.trading_classes import StockError, StockButton

from lib.utils.trading_utils import Stock, choose_two, to_stock, seconds_until, create_poll_embed, \
    create_database_poll_entry, get_all_stocks_from_db


class Trading(Cog):
    def __init__(self, bot):
        self.bot = bot
        api_key_id = 'PKZ0AFHB21M8WVI8UMX3'
        api_secret_key = 'AXBHvjLKqMQPQDEwosddasP0CZqjAUuvV6trCy3x'
        endpoint = URL('https://paper-api.alpaca.markets')
        self.api = alpaca_trade_api.REST(key_id=api_key_id, secret_key=api_secret_key, base_url=endpoint)
        self.pinned_message: Message | None = None
        self.create_poll_loop.start()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("trading")

    def update_stocks(self) -> None:
        all_assets: list[Asset] = self.api.list_assets(status='active', asset_class='us_equity')
        relevant_assets = list(filter(lambda a: a.fractionable and a.tradable and a.status == 'active', all_assets))
        insert_statement = 'INSERT INTO assets (id, symbol) VALUES (?, ?)'

        db.execute('DELETE FROM assets')
        db.multiexec(insert_statement, map(lambda a: (a.id, a.symbol), relevant_assets))

    def buy_stock(self, stock: Stock):
        response: Order = self.api.submit_order(symbol=stock.symbol,
                                                notional=1.,
                                                side='buy',
                                                type='market',
                                                time_in_force='day',
                                                order_class='simple')
        print(response)
        if response.status != 'accepted':
            raise StockError('Order not accepted')

    @tasks.loop(hours=24)
    async def create_poll_loop(self):
        await asyncio.sleep(seconds_until(9, 0))  # Will stay here until your clock says 11:58
        spam = await self.bot.fetch_channel(705425949541269668)
        print(f'creating poll')
        await self._create_poll(spam, 705425948996272210)

    @command()
    @has_permissions(administrator=True)
    async def create_poll(self, ctx: Context):
        await self._create_poll(ctx.channel, ctx.guild.id)

    async def _create_poll(self, channel: TextChannel, guild_id: int):
        stocks = get_all_stocks_from_db()
        chosen_stocks = choose_two(stocks)
        if not chosen_stocks:
            self.update_stocks()
            stocks = get_all_stocks_from_db()
            chosen_stocks = choose_two(stocks)
            if not chosen_stocks:
                await channel.send('No Stocks found :(')
                return

        stock1 = to_stock(chosen_stocks[0])
        stock2 = to_stock(chosen_stocks[1])

        poll_id, end_time = create_database_poll_entry(guild_id, stock1, stock2)

        embed1 = create_poll_embed(stock1, end_time)
        embed2 = create_poll_embed(stock2, end_time)

        view = discord.ui.View(timeout=None)
        view.add_item(StockButton(stock1.symbol, stock1.id, poll_id))
        view.add_item(StockButton(stock2.symbol, stock2.id, poll_id))

        # add job for evaluation
        self.bot.scheduler.add_job(
            func=self.evaluate_poll,
            trigger=DateTrigger(end_time),
            args=[poll_id, channel])
        message: Message = await channel.send(embeds=[embed1, embed2], view=view)
        self.pinned_message = message
        await message.pin()

    async def evaluate_poll(self, poll_id: int, channel: TextChannel):
        poll_record = db.record('SELECT start_time, end_time, asset1_id, asset2_id FROM trading_polls WHERE poll_id =?',
                                poll_id)
        if poll_record is None:
            await channel.send(f'Couldn\'t find poll with id {poll_id}')
            return
        start_time, end_time, asset1_id, asset2_id = poll_record

        count1 = db.field('SELECT COUNT (*) FROM trading_votes WHERE poll_id = ? AND asset_id = ?',
                          poll_id, asset1_id)

        count2 = db.field('SELECT COUNT (*) FROM trading_votes WHERE poll_id = ? AND asset_id = ?',
                          poll_id, asset2_id)

        symbol1 = db.field('SELECT symbol FROM assets WHERE id = ?', asset1_id)
        symbol2 = db.field('SELECT symbol FROM assets WHERE id = ?', asset2_id)
        stock1 = to_stock((asset1_id, symbol1))
        stock2 = to_stock((asset2_id, symbol2))
        if count1 > count2:
            winner: Stock = stock1
        else:
            winner: Stock = stock2
        try:
            self.buy_stock(winner)
        except StockError:
            await channel.send(f'Order for Stock Voting Winner **${winner.symbol}** not accepted :(')
            return
        await channel.send(f'Bought $1 of Stock Voting Winner **${winner.symbol}** at current price ${winner.currentPrice}')
        if self.pinned_message and self.pinned_message.pinned:
            await self.pinned_message.unpin()


def setup(bot):
    bot.add_cog(Trading(bot))
