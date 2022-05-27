import dataclasses
from discord import Embed, HTTPException, Interaction, ui, enums

from lib.db import db


@dataclasses.dataclass
class Stock:
    id: str
    symbol: str
    shortName: str
    description: str
    logo_url: str
    currentPrice: float
    marketCap: float


class StockError(Exception):
    pass


class StockButton(ui.Button):
    def __init__(self, symbol: str, stock_id: str, poll_id: int):
        """A button for one role. `custom_id` is needed for persistent views."""
        self.poll_id = poll_id
        self.stock_id = stock_id
        self.symbol = symbol
        super().__init__(
            label=symbol,
            style=enums.ButtonStyle.primary,
            custom_id=stock_id,
        )

    async def callback(self, interaction: Interaction):
        """This function will be called any time a user clicks on this button."""
        existing_vote = db.field('SELECT asset_id FROM trading_votes WHERE poll_id = ? AND user_id = ?',
                                 self.poll_id, interaction.user.id)
        current_count = count_votes(self.poll_id, self.stock_id)

        embeds = interaction.message.embeds
        this_embed: Embed = [e for e in embeds if e.title == self.symbol].pop()
        other_embed: Embed = [e for e in embeds if e.title != self.symbol].pop()
        message = f'{interaction.user.mention} voted to buy **${self.symbol}**!'
        if existing_vote is not None:
            if existing_vote == self.stock_id:
                return
            message = await self._handle_vote_change(existing_vote, interaction, other_embed)

        # insert new vote
        db.execute('INSERT INTO trading_votes (poll_id, user_id, asset_id)  VALUES (?, ?, ?)',
                   self.poll_id, interaction.user.id, self.stock_id)

        # update count in embed
        this_embed.remove_field(3)
        this_embed.add_field(name='Current Votes', value=str(current_count + 1))

        await interaction.message.edit(embeds=embeds)
        # await interaction.response.send(message)
        await dummy_response(interaction)

    async def _handle_vote_change(self, existing_vote: str, interaction: Interaction, other_embed: Embed) -> str:
        # remove other vote and get it's new amount
        db.execute('DELETE FROM trading_votes WHERE poll_id = ? AND user_id = ? AND asset_id = ?',
                   self.poll_id, interaction.user.id, existing_vote)
        reduced_count = count_votes(self.poll_id, existing_vote)
        # update other embed
        other_embed.remove_field(3)
        other_embed.add_field(name='Current Votes', value=str(reduced_count))
        return f'{interaction.user.mention} changed their vote to **${self.symbol}**!'


def count_votes(poll_id: int, asset_id: str) -> int:
    return db.field('SELECT COUNT (*) FROM trading_votes WHERE poll_id = ? AND asset_id = ?',
                    poll_id, asset_id)


async def dummy_response(interaction: Interaction):
    try:
        await interaction.response.send_message()
    except HTTPException:
        pass
