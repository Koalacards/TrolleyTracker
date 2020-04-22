import discord
from discord.ext import commands

from minigame import MiniGame
import globalvars

'''
TODO:Functionality that should be added:
    -a role to not be invited to multiplayer games that the user can toggle
    -a check that each user has DM's open before playing any game that involves DM's
        -an alternate way of doing this is making the channels non-read for players who arent inputting to the game
    
'''

client = commands.Bot(command_prefix = globalvars.PREFIX)

@client.event
async def on_ready():
    print('TrolleyTracker v0.2.1')

@client.command()
async def clear(ctx, amount=20):
    if str(ctx.message.author) == 'Koalacards#4618':
        await ctx.channel.purge(limit=amount)

@client.command()
async def reset(ctx):
    await ctx.message.delete()
    if str(ctx.message.author) == 'Koalacards#4618':
        guild = ctx.message.guild
        for role in guild.roles:
            for gameStr in globalvars.GAMES_LIST:
                if gameStr in str(role):
                    await role.delete()
        
        for channel in ctx.message.channel.category.channels:
            for gameStr in globalvars.GAMES_LIST:
                if gameStr in channel.name:
                    await channel.delete()
        globalvars.JUNGLE_NUMS = []
        globalvars.TAG_NUMS = []

@client.command()
async def play(ctx, *, game):
    if ctx.message.channel.id not in globalvars.COMMAND_CHANNEL_IDS:
        return
    gamelower = game.lower()
    gamestripped = gamelower.strip()
    gamefinal = gamestripped.replace(' ', '')
    await ctx.message.delete()
    if gamefinal == 'junglevines':
        if checkUserEligible(ctx.message.author) == False:
            await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active minigame channel! You must complete that game to be a part of another one.')
            return
        newGame = MiniGame(ctx, client, gamefinal, 1, 1)
        await newGame.createChannel()
        return
    elif gamefinal == 'iceslide':
        await ctx.send('Ice slide is still in development.')
    elif gamefinal == 'tag':
        if checkUserEligible(ctx.message.author) == False:
            await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active minigame channel! You must complete that game to be a part of another one.')
            return
        newGame = MiniGame(ctx, client, gamefinal, 2, 2)
        await newGame.createChannel()
    else:
        await ctx.send(f'Invalid game selected. Enter "{globalvars.PREFIX}help" for help.')

#Checks to see if a user is eligible to be a part of a 
def checkUserEligible(member):
    for role in member.roles:
        for gameStr in globalvars.GAMES_LIST:
            if gameStr in str(role):
                return False
    return True
client.run(globalvars.RUN_ID)