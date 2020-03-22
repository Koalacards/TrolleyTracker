import discord
from discord.ext import commands

from junglevines import JungleVines

client = commands.Bot(command_prefix = 'koalabot ')

@client.event
async def on_ready():
    print('KoalaBot v0.1')

@client.command()
async def ping(ctx):
    await ctx.send('pong')

@client.command()
async def play(ctx, *, game):
    gamelower = game.lower()
    gamestripped = gamelower.strip()
    gamefinal = gamestripped.replace(' ', '')
    response = ''
    if gamefinal == 'junglevines':
        response = 'booting up jungle vines'
    elif gamefinal == 'iceslide':
        response = 'booting up ice slide'
    elif gamefinal == 'tag':
        response = 'booting up tag'
    else:
        response = 'invalid game selected. your options are junglevines and iceslide'
    await ctx.send(response)
client.run('NjM1NTg2MjY0OTIxNDA3NTIy.Xl3Irw.JX2w5a-A4iS_dITjQTcj9fEs630')