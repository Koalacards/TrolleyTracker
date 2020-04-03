import discord
from discord.ext import commands

from junglevines import JungleVines
import globalvars

client = commands.Bot(command_prefix = 'koalabot ')

@client.event
async def on_ready():
    print('KoalaBot v0.1')

@client.command()
async def clear(ctx, amount=20):
    await ctx.channel.purge(limit=amount)

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
    await ctx.message.delete()
    if gamefinal == 'junglevines':
        for role in ctx.message.author.roles:
            if 'junglevines' in str(role):
                await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active game of junglevines! You must complete that game to create another one.')
                return
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