from peewee import  *
from db.dbmodels import *

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
        ActiveGameChannels.create(channel_id=channel_id)
    else:
        return

def remove_game_channel(channel_id: int) -> None:
    """Remove a game channel from the database."""
    query = ActiveGameChannels.delete().where(ActiveGameChannels.channel_id == channel_id)
    query.execute()