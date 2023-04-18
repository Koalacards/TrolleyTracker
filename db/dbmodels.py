from peewee import *

database = SqliteDatabase('db/trolleydata.db')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class ActiveGameChannels(BaseModel):
    channel_id = IntegerField(null=True)
    game_data = TextField(null=True)
    time = TextField(null=True)

    class Meta:
        table_name = 'ActiveGameChannels'
        primary_key = False

class CannonGameLeaderboards(BaseModel):
    rounds_to_win = IntegerField(null=True)
    user_id = IntegerField(null=True)

    class Meta:
        table_name = 'CannonGame Leaderboards'
        primary_key = False

class JungleVinesBananasLeaderboard(BaseModel):
    bananas = IntegerField(null=True)
    user_id = IntegerField(null=True)

    class Meta:
        table_name = 'JungleVines Bananas Leaderboard'
        primary_key = False

class JungleVinesTimeLeaderboards(BaseModel):
    time_to_win = IntegerField(null=True)
    user_id = IntegerField(null=True)

    class Meta:
        table_name = 'JungleVines Time Leaderboards'
        primary_key = False

