import discord

from typing import Optional

def create_embed(
    title: str, description: str, color: discord.Color
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

async def send(
    interaction: discord.Interaction,
    embed: discord.Embed,
    file: Optional[discord.File] = None,
    view: Optional[discord.ui.View] = None,
    ephemeral: bool = False,
):
    kwargs = {}
    kwargs["embed"] = embed
    kwargs["ephemeral"] = ephemeral
    if file:
        kwargs["file"] = file
    if view:
        kwargs["view"] = view

    await interaction.response.send_message(**kwargs)