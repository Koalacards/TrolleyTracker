import discord
from discord.ext import commands

from junglevines import JungleVines
from tag import Tag
import globalvars

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
        if checkUserEligible(ctx.message.author) == False:
            await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active minigame channel! You must complete that game to be a part of another one.')
            return
        newGame = JungleVines(ctx, client)
        await newGame.createChannel()
        return
    elif gamefinal == 'iceslide':
        await ctx.send('Ice slide is still in development.')
    elif gamefinal == 'tag':
        if checkUserEligible(ctx.message.author) == False:
            await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active minigame channel! You must complete that game to be a part of another one.')
            return
        newGame = Tag(ctx, client)
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