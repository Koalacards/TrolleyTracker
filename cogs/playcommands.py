import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from globalvars import GAMES_CHOICES
import logger
from games.minigame import MiniGame
from utils import create_embed, send
from views import url_view

class PlayCommands(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @app_commands.command(name="play")
    @app_commands.describe(game="The game you wish to play!")
    @app_commands.choices(game=GAMES_CHOICES)
    async def play(self, interaction:discord.Interaction, game: Choice[int]):
        """Play a trolley game!"""
        await logger.log(f"New game: {game.name} created by {interaction.user.name}", self.client)
        new_game = MiniGame(interaction, game.name)
        await new_game.createChannel()
        await send(interaction, create_embed("Success!", f"You have created a game of {game.name}- check your pings in this category to see which channel you're in!", discord.Color.green()), view=url_view)

async def setup(client: commands.Bot):
    await client.add_cog(PlayCommands(client))