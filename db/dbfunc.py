from peewee import  *
from db.dbmodels import *
from datetime import datetime
from utils import str2dict, str2datetime

def is_game_channel(channel_id:int) -> bool:
    """Was the given channel id a trolley channel or not?"""
    query = ActiveGameChannels.select().where(ActiveGameChannels.channel_id == channel_id)
    if len(query) == 0:
        return False
    else:
        return True

def add_game_channel(channel_id:int) -> None:
    """Add a game channel to the database."""
    query = ActiveGameChannels.select().where(ActiveGameChannels.channel_id == channel_id)
    if len(query) == 0:
        ActiveGameChannels.create(channel_id=channel_id, time=str(datetime.now()), game_data = {})
    else:
        return

def remove_game_channel(channel_id: int) -> None:
    """Remove a game channel from the database."""
    query = ActiveGameChannels.delete().where(ActiveGameChannels.channel_id == channel_id)
    query.execute()


def set_channel_time(channel_id: int, time: str):
    query = ActiveGameChannels.update(time=time).where(ActiveGameChannels.channel_id == channel_id)
    query.execute()


def get_channel_time(channel_id: int):
    query = ActiveGameChannels.select().where(ActiveGameChannels.channel_id == channel_id)
    if len(query) > 0:
        for item in query:
            return str2datetime(item.time)


def set_channel_game_data(channel_id: int, game_data: str):
    query = ActiveGameChannels.update(game_data=game_data).where(ActiveGameChannels.channel_id == channel_id)
    query.execute()


def get_channel_game_data(channel_id: int):
    query = ActiveGameChannels.select().where(ActiveGameChannels.channel_id == channel_id)
    if len(query) > 0:
        for item in query:
            return str2dict(item.game_data)