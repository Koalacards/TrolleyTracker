import discord
from discord.ext import commands

client = commands.Bot(command_prefix = 'koalabot ')

@client.event
async def on_ready():
    print('KoalaBot v0.1')

@client.command()
async def ping(ctx):
    await ctx.send('pong')

@client.command()
async def play(ctx, *, game):
    response = ''
    if game == 'junglevines':
        response = 'booting up jungle vines'
    elif game == 'iceslide':
        response = 'booting up ice slide'
    else:
        response = 'invalid game selected. your options are junglevines and iceslide'
    await ctx.send(response)
client.run('NjM1NTg2MjY0OTIxNDA3NTIy.Xl3Irw.JX2w5a-A4iS_dITjQTcj9fEs630')