import globalvars
from discord.ext import commands

async def log(text:str, client: commands.Bot):
    logs_channel = client.get_channel(globalvars.LOGS_CHANNEL)
    await logs_channel.send(text)
