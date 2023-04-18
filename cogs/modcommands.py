import discord
from discord import app_commands
from discord.ext import commands
import logger
from db.dbfunc import is_game_channel
from utils import create_embed, send
from views import url_view

class ModCommands(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @app_commands.command(name="shutdown-channel")
    @app_commands.describe(channel="Which channel to shutdown")
    @app_commands.default_permissions(manage_guild=True)
    async def reset(self, interaction:discord.Interaction, channel:discord.TextChannel):
        """Mod Command: Deletes a trolley game channel."""
        if is_game_channel(channel.id):
            await logger.log(f'{interaction.user.name} has reset channel {channel.name}', self.client)
            await channel.delete()
            await send(interaction, create_embed("Channel deleted successfully", "", discord.Color.green()), ephemeral=True)

async def setup(client: commands.Bot):
    await client.add_cog(ModCommands(client))