import datetime
import globalvars
import discord

async def log(text:str, guild:discord.Guild):
    now = datetime.datetime.now()
    try:
        if globalvars.LOGS_CHANNEL is None:
            globalvars.LOGS_CHANNEL = discord.utils.get(guild.channels, name=globalvars.LOGS_CHANNEL_NAME)
        await globalvars.LOGS_CHANNEL.send(f'{str(now)}: {text}')
        print(f'{str(now)}: {text}')
    except: 
        print(f'{str(now)}: {text}')
        print()
