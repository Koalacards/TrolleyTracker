import discord
from discord import app_commands
from discord.ext import commands

from utils import create_embed, send
from views import url_view
from globalvars import SUGGESTION_CHANNEL
import logger

class UtilityCommands(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        """Send a ping to the TrolleyTracker."""
        await send(interaction, create_embed("Pong!", f"TrolleyTracker's latency is {self.client.latency}!", discord.Color.green()), view=url_view)
    
    
    @app_commands.command(name="pong")
    async def pong(self, interaction: discord.Interaction):
        """Send a pong to the TrolleyTracker (this is totally different than ping, I promise)."""
        await send(interaction, create_embed("Ping!", f"TrolleyTracker's latency is {self.client.latency}!", discord.Color.green()), view=url_view)
    
    
    #Allow users to put in suggestions directly through the bot
    @app_commands.command(name="suggest")
    @app_commands.describe(suggestion="Something to suggest to the TrolleyTracker devs!")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        """Suggest an improvement or bug relating to TrolleyTracker!"""
        suggestion_channel = self.client.get_channel(SUGGESTION_CHANNEL)
        if suggestion is not None and suggestion != '':
            suggestionEmbed = create_embed(
                title=f'New Suggestion from {interaction.user.name}!',
                description = suggestion,
                color=discord.Color.purple()
            )
            await suggestion_channel.send(embed=suggestionEmbed)

            recievedSuggestionEmbed = create_embed(
                title='Success!',
                description="Your suggestion or report has been sent to the devs, thank you for supporting TrolleyTracker!",
                color=discord.Color.green()
            )
            await send(interaction, embed=recievedSuggestionEmbed, view=url_view, ephemeral=True)
    

    @app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction):
        """Displays the commands to use TrolleyTracker!"""
        author = interaction.user
        if author.guild_permissions.administrator or author.guild_permissions.manage_guild:
            await send(interaction, embed=mod_help_embed(), view=url_view, ephemeral=True)
            await logger.log(f'mod help command called by {author.name}', self.client)
        else:
            await send(interaction, embed=reg_help_embed(), view=url_view)
            await logger.log(f'regular help command called by {author.name}', self.client)

async def setup(client: commands.Bot):
    await client.add_cog(UtilityCommands(client))


def reg_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title='TrolleyTracker Help Page',
        description=f'To start a game, type `/play` and pick a game from the list!\n**Note**: for multiplayer games, you must have server member DM permissions on.',
        colour=discord.Color.purple()
    )
    embed.add_field(name='Single-Player Games:', value='-Jungle Vines\n-Cannon Game', inline=True)
    embed.add_field(name='Multi-Player Games:', value='-Tag (2 players)\n-Ice Slide (2-8 players)', inline=True)
    embed.add_field(name='Other Commands:', value=f'-`/suggest [message]`: Put any suggestion you have for the bot in here and it will be recorded!', inline=False)
    return embed


def mod_help_embed() -> discord.Embed:
    embed = reg_help_embed()
    embed.add_field(name='Moderator Commands', value=f'-`/reset [Channel Name]`: shuts down a game channel')
    return embed