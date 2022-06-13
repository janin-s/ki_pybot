import discord

from dataclasses import dataclass
from datetime import datetime
from discord import Role, enums, Interaction
from lib.utils.utils import dummy_response


@dataclass
class Event:
    guild_id: int
    channel_id: int
    message_id: int
    event_id: int
    role_id: int
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str

    def __init__(self, guild_id: int, channel_id: int, message_id: int, event_id: int, role_id: int, name: str,
                 description: str, start_time: str, end_time: str, location: str):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.event_id = event_id
        self.role_id = role_id
        self.name = name
        self.description = description
        self.start_time = datetime.fromisoformat(start_time)
        self.end_time = datetime.fromisoformat(end_time)
        self.location = location

    def __str__(self) -> str:
        return f'{self.name}: {self.description}, from {self.start_time.strftime("%H.%M %d.%m.%y")} to ' \
               f'{self.end_time.strftime("%H.%M %d.%m.%y")} at {self.location}'


class EventView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class EventButton(discord.ui.Button):
    def __init__(self, role: Role, event_id: int, mode: str):
        self.role = role
        self.mode = mode
        super().__init__(
            label=mode.upper(),
            style=enums.ButtonStyle.primary,
            custom_id=str(event_id) + mode,
        )

    async def callback(self, interaction: Interaction):
        """This function will be called any time a user clicks on this button."""
        if self.mode == 'join':
            if self.role not in interaction.user.roles:
                await interaction.user.add_roles(self.role, atomic=True)
        else:
            if self.role in interaction.user.roles:
                await interaction.user.remove_roles(self.role, atomic=True)

        await dummy_response(interaction)
