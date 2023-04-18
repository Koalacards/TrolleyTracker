import discord
import json
from datetime import datetime

from typing import Optional, Dict

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

def str2dict(dict_str: str) -> Dict:
    json_compatible = dict_str.replace("'", '"')
    new_dict = json.loads(json_compatible)
    return new_dict


def datetime2str(datetime: datetime) -> str:
    year = datetime.year
    month = datetime.month
    day = datetime.day
    hour = datetime.hour
    minute = datetime.minute
    second = datetime.second
    microsecond = datetime.microsecond
    list_format = [year, month, day, hour, minute, second, microsecond]
    return str(list_format)

def str2datetime(datetime_str: str) -> datetime:
    json_compatible = datetime_str.replace("'", '"')
    dt_list = json.loads(json_compatible)
    year, month, day, hour, minute, second, microsecond = int(dt_list[0]), int(dt_list[1]), int(dt_list[2]), int(dt_list[3]), int(dt_list[4]), int(dt_list[5]), int(dt_list[6])
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond)