import discord
from discord.ext import commands
import logger
import asyncio

from minigame import MiniGame
import helpEmbed
import globalvars
import confidential

'''
TODO:Functionality that should be added:
    -a check that each user has DM's open before playing any game that involves DM's
        -an alternate way of doing this is making the channels non-read for players who arent inputting to the game
    
'''

client = commands.Bot(command_prefix = globalvars.PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    print('TrolleyTracker v0.5')

#This isnt supposed to do anything, this is exclusively to remove an error from the console
@client.command()
async def invite(ctx, *, bs):
    #do nothing lol
    pass

#Allow users to put in suggestions directly through the bot
@client.command()
async def suggest(ctx, *, suggestion):
    if ctx.message.channel.id not in globalvars.COMMAND_CHANNEL_IDS:
        return
    await ctx.message.delete()
    suggestion_channel = discord.utils.get(ctx.guild.channels, id=globalvars.SUGGESTION_CHANNEL)
    if suggestion is not None and suggestion != '':
        recievedSuggestionEmbed = discord.Embed(
            title=f'Thank you, your suggestion has been recorded!',
            colour=discord.Color.green()
        )
        message = await ctx.send(embed=recievedSuggestionEmbed)
        suggestionEmbed = discord.Embed(
            title='New Suggestion!',
            description = f'**From**: {ctx.message.author.display_name} \n`{str(suggestion)}`',
            colour=discord.Color.purple()
        )
        await suggestion_channel.send(embed=suggestionEmbed)

        await asyncio.sleep(3)

        await message.delete()

@client.command()
async def clear(ctx, amount=20):
    await ctx.message.delete()
    if hasPermission(ctx.message.author):
        await ctx.channel.purge(limit=amount)
        logger.log(f'{amount} messages cleared by {ctx.message.author.display_name}')

@client.command()
async def help(ctx):
    if ctx.message.channel.id not in globalvars.COMMAND_CHANNEL_IDS:
        return
    if hasPermission(ctx.message.author):
        await ctx.channel.send(embed=helpEmbed.modHelpEmbed())
        logger.log(f'mod help command called by {ctx.message.author.display_name}')
    else:
        await ctx.channel.send(embed=helpEmbed.regHelpEmbed())
        logger.log(f'regular help command called by {ctx.message.author.display_name}')

@client.command()
async def noinvites(ctx):
    if ctx.message.channel.id not in globalvars.COMMAND_CHANNEL_IDS:
        return
    guild = ctx.message.guild
    #check to see if the user already has the role
    author = ctx.message.author
    for role in author.roles:
        if str(role) == 'noinvites':
            await ctx.message.channel.send(f'You already have the noinvites role, {author.display_name}!')
            return
    #check to see if there is a noinvites role set in place
    noInvitesRole = None
    for role in guild.roles:
        if str(role) == 'noinvites':
            noInvitesRole = role
    #create the role if needed
    if noInvitesRole is None:
        noInvitesRole = await guild.create_role(name='noinvites')
    #add the role to the member
    await author.add_roles(noInvitesRole)
    logger.log(f'the noinvites role has been added to {author.display_name}')
    embed=discord.Embed(
        title=f'The noinvites role has been added, {author.display_name}!\n Use `{globalvars.PREFIX}invites` to remove the noinvites role.',
        colour=discord.Color.green()
    )
    await ctx.message.channel.send(embed=embed)


@client.command()
async def invites(ctx):
    if ctx.message.channel.id not in globalvars.COMMAND_CHANNEL_IDS:
        return
    author = ctx.message.author
    channel = ctx.message.channel
    for role in author.roles:
        if str(role) == 'noinvites':
            await author.remove_roles(role)
            logger.log(f'the noinvites role has been removed from {author.display_name}')
            embed=discord.Embed(
                title=f'The noinvites role has been removed, {author.display_name}!\n Use `{globalvars.PREFIX}noinvites` to re-add the noinvites role.',
                colour=discord.Color.green()
            )
            await channel.send(embed=embed)
            return
    await channel.send(f'You already dont have the noinvites role, {author.display_name}!')
    
@client.command()
async def reset(ctx, channelName):
    await ctx.message.delete()
    if hasPermission(ctx.message.author):
        logger.log(f'{ctx.message.author.display_name} has reset channel {channelName}')
        guild = ctx.message.guild
        for role in guild.roles:
            if str(role) == channelName:
                await role.delete()

        for channel in ctx.message.channel.category.channels:
            if channel.name == channelName:
                await channel.delete()

        number = int(channelName[-4:])
        if channelName.split('-')[0] == 'junglevines':
            globalvars.JUNGLE_NUMS.remove(number)
        if channelName.split('-')[0] == 'tag':
            globalvars.TAG_NUMS.remove(number)   
        if channelName.split('-')[0] == 'iceslide':
            globalvars.ICE_SLIDE_NUMS.remove(number)
        if channelName.split('-')[0] == 'cannongame':
            globalvars.CANNON_NUMS.remove(number)     

@client.command()
async def resetall(ctx):
    await ctx.message.delete()
    if hasPermission(ctx.message.author):
        logger.log(f'{ctx.message.author.display_name} has reset all channels')
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
        logger.log(f'new game of Jungle Vines created by {ctx.message.author.display_name}')
        newGame = MiniGame(ctx, client, gamefinal, 1, 1)
        await newGame.createChannel()
        return
    elif gamefinal == 'iceslide':
        if checkUserEligible(ctx.message.author) == False:
            await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active minigame channel! You must complete that game to be a part of another one.')
            return
        logger.log(f'new game of Ice Slide created by {ctx.message.author.display_name}')
        newGame = MiniGame(ctx, client, gamefinal, 2, 8)
        await newGame.createChannel()
    elif gamefinal == 'tag':
        if checkUserEligible(ctx.message.author) == False:
            await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active minigame channel! You must complete that game to be a part of another one.')
            return
        logger.log(f'new game of Tag created by {ctx.message.author.display_name}')
        newGame = MiniGame(ctx, client, gamefinal, 2, 2)
        await newGame.createChannel()
    elif gamefinal == 'cannongame':
        if checkUserEligible(ctx.message.author) == False:
            await ctx.send(f'Sorry <@{ctx.message.author.id}>, you are already in an active minigame channel! You must complete that game to be a part of another one.')
            return
        logger.log(f'new game of Cannon Game created by {ctx.message.author.display_name}')
        newGame = MiniGame(ctx, client, gamefinal, 1, 1)
        await newGame.createChannel()
    else:
        await ctx.send(f'Invalid game selected. Enter `{globalvars.PREFIX}help` for help.')

#Checks to see if a user is eligible to be a part of a 
def checkUserEligible(member):
    for role in member.roles:
        for gameStr in globalvars.GAMES_LIST:
            if gameStr in str(role):
                return False
    return True

#checks to see if the user that entered the command has permission to
def hasPermission(member):
    for role in member.roles:
        if str(role) in globalvars.EXTRA_PERMS:
            return True
    return False
client.run(confidential.RUN_ID)