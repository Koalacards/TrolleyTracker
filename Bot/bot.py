import discord
from discord.ext import commands

from junglevines import JungleVines
import globalvars

client = commands.Bot(command_prefix = 'koalabot ')

@client.event
async def on_ready():
    print('KoalaBot v0.1')

@client.command()
async def ping(ctx):
    await ctx.send('pong')

@client.command()
async def play(ctx, *, game):
    if ctx.message.channel.id not in globalvars.COMMAND_CHANNEL_IDS:
        return
    gamelower = game.lower()
    gamestripped = gamelower.strip()
    gamefinal = gamestripped.replace(' ', '')
    response = ''
    if gamefinal == 'junglevines':
        newGame = JungleVines(ctx, client)
        await newGame.createChannel()
        return
    elif gamefinal == 'iceslide':
        response = 'booting up ice slide'
    elif gamefinal == 'tag':
        response = 'booting up tag'
    else:
        response = 'invalid game selected. your options are junglevines and iceslide'
    await ctx.send(response)
client.run(globalvars.RUN_ID)