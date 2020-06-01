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
    print('TrolleyTracker v0.5.3')

#This isnt supposed to do anything, this is exclusively to remove an error from the console
@client.command()
async def invite(ctx, *, bs):
    #do nothing lol
    pass

#Allow users to put in suggestions directly through the bot
@client.command()
async def suggest(ctx, *, suggestion):
    if ctx.message.channel.name != globalvars.COMMAND_CHANNEL_NAME:
        return
    await ctx.message.delete()
    suggestion_channel = discord.utils.get(ctx.guild.channels, name=globalvars.SUGGESTION_CHANNEL_NAME)
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
async def help(ctx):
    if ctx.message.channel.name != globalvars.COMMAND_CHANNEL_NAME:
        return
    if hasPermission(ctx.message.author):
        player = ctx.message.author
        await ctx.channel.send(embed=helpEmbed.regHelpEmbed())
        if player.dm_channel is None:
            await player.create_dm()
        await player.dm_channel.send(embed=helpEmbed.modHelpEmbed())
        await logger.log(f'mod help command called by {ctx.message.author.display_name}', ctx.message.guild)
    else:
        await ctx.channel.send(embed=helpEmbed.regHelpEmbed())
        await logger.log(f'regular help command called by {ctx.message.author.display_name}', ctx.message.guild)

'''
@client.command()
async def noinvites(ctx):
    if ctx.message.channel.name != globalvars.COMMAND_CHANNEL_NAME:
        return
    guild = ctx.message.guild
    #check to see if the user already has the role
    author = ctx.message.author
    for role in author.roles:
        if str(role) == 'noinvites':
            alreadyHaveRoleEmbed = discord.Embed(
                title=f'You already have the noinvites role, {author.display_name}!',
                colour=discord.Color.red()
            )
            await ctx.message.channel.send(embed=alreadyHaveRoleEmbed)
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
    await logger.log(f'the noinvites role has been added to {author.display_name}', guild)
    embed=discord.Embed(
        title=f'The noinvites role has been added, {author.display_name}!\n Use `{globalvars.PREFIX}invites` to remove the noinvites role.',
        colour=discord.Color.green()
    )
    await ctx.message.channel.send(embed=embed)
'''
'''
@client.command()
async def invites(ctx):
    if ctx.message.channel.name != globalvars.COMMAND_CHANNEL_NAME:
        return
    author = ctx.message.author
    channel = ctx.message.channel
    for role in author.roles:
        if str(role) == 'noinvites':
            await author.remove_roles(role)
            await logger.log(f'the noinvites role has been removed from {author.display_name}', ctx.message.guild)
            embed=discord.Embed(
                title=f'The noinvites role has been removed, {author.display_name}!\n Use `{globalvars.PREFIX}noinvites` to re-add the noinvites role.',
                colour=discord.Color.green()
            )
            await channel.send(embed=embed)
            return
    alreadyHaveRoleEmbed = discord.Embed(
        title=f'You already dont have the noinvites role, {author.display_name}!',
        colour=discord.Color.red()
    )
    await channel.send(embed=alreadyHaveRoleEmbed)
'''  
@client.command()
async def reset(ctx, channelName):
    await ctx.message.delete()
    if hasPermission(ctx.message.author):
        await logger.log(f'{ctx.message.author.display_name} has reset channel {channelName}', ctx.message.guild)
        guild = ctx.message.guild

        '''
        for role in guild.roles:
            if str(role) == channelName:
                await role.delete()
        '''

        tag = discord.utils.get(guild.roles, name='tag')
        for channel in guild.channels:
            if channel.name == channelName:
                overrides = channel.overwrites
                for overriddenMember in overrides.keys():
                    if isinstance(overriddenMember, discord.Member) and tag in overriddenMember.roles:
                        await overriddenMember.remove_roles(tag)
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
        if channelName.split('-')[0] == 'matchminnie':
            globalvars.MATCH_MINNIE_NUMS.remove(number)        

@client.command()
async def resetall(ctx):
    await ctx.message.delete()
    if hasPermission(ctx.message.author):
        await logger.log(f'{ctx.message.author.display_name} has reset all channels', ctx.message.guild)
        guild = ctx.message.guild

        '''
        for role in guild.roles:
            for gameStr in globalvars.GAMES_LIST:
                if gameStr in str(role):
                    await role.delete()
        '''
        role = discord.utils.get(guild.roles, name='tag')
        for member in role.members:
            await member.remove_roles(role)
        
        for channel in guild.channels:
            for gameStr in globalvars.GAMES_LIST:
                if gameStr in channel.name:
                    await channel.delete()
        globalvars.JUNGLE_NUMS = []
        globalvars.TAG_NUMS = []

@client.command()
async def play(ctx, *, game):
    if ctx.message.channel.name != globalvars.COMMAND_CHANNEL_NAME:
        print(ctx.message.channel.name)
        return
    gamelower = game.lower()
    gamestripped = gamelower.strip()
    gamefinal = gamestripped.replace(' ', '')
    inAnotherGameEmbed = discord.Embed(
        title=f'Sorry {ctx.message.author.display_name}, you are already in {globalvars.NUM_GAMES_ALLOWED} active minigame channel(s)! You must finish your other game(s) before starting this one.',
        colour=discord.Color.red()
    )
    await ctx.message.delete()
    if gamefinal == 'junglevines':
        if numGamesPlaying(ctx.message.author) >= globalvars.NUM_GAMES_ALLOWED:
            message = await ctx.send(embed=inAnotherGameEmbed)
            await asyncio.sleep(5)
            await message.delete()
            return
        await logger.log(f'new game of Jungle Vines created by {ctx.message.author.display_name}', ctx.message.guild)
        newGame = MiniGame(ctx, client, gamefinal, 1, 1)
        await newGame.createChannel()
        return
    elif gamefinal == 'iceslide':
        if numGamesPlaying(ctx.message.author) >= globalvars.NUM_GAMES_ALLOWED:
            message = await ctx.send(embed=inAnotherGameEmbed)
            await asyncio.sleep(5)
            await message.delete()
            return
        await logger.log(f'new game of Ice Slide created by {ctx.message.author.display_name}', ctx.message.guild)
        newGame = MiniGame(ctx, client, gamefinal, 2, 8)
        await newGame.createChannel()
    elif gamefinal == 'tag':
        if numGamesPlaying(ctx.message.author) >= globalvars.NUM_GAMES_ALLOWED:
            message = await ctx.send(embed=inAnotherGameEmbed)
            await asyncio.sleep(5)
            await message.delete()
            return
        await logger.log(f'new game of Tag created by {ctx.message.author.display_name}', ctx.message.guild)
        newGame = MiniGame(ctx, client, gamefinal, 2, 2)
        await newGame.createChannel()
    elif gamefinal == 'cannongame':
        if numGamesPlaying(ctx.message.author) >= globalvars.NUM_GAMES_ALLOWED:
            message = await ctx.send(embed=inAnotherGameEmbed)
            await asyncio.sleep(5)
            await message.delete()
            return
        await logger.log(f'new game of Cannon Game created by {ctx.message.author.display_name}', ctx.message.guild)
        newGame = MiniGame(ctx, client, gamefinal, 1, 1)
        await newGame.createChannel()
    elif gamefinal == 'matchminnie':
        message = await ctx.send('Uh oh, you found my secret new project! Don\'t tell anyone shhhh')
        await asyncio.sleep(2)
        await message.delete()
        '''
        if numGamesPlaying(ctx.message.author) >= globalvars.NUM_GAMES_ALLOWED:
            message = await ctx.send(embed=inAnotherGameEmbed)
            await asyncio.sleep(5)
            await message.delete()
            return
        await logger.log(f'new game of Match Minnie created by {ctx.message.author.display_name}', ctx.message.guild)
        newGame = MiniGame(ctx, client, gamefinal, 2, 4)
        await newGame.createChannel()
        '''
    else:
        invalidGameEmbed = discord.Embed(
            title=f'Invalid game selected. Enter `{globalvars.PREFIX}help` for help.',
            colour=discord.Color.red()
        )
        await ctx.send(embed=invalidGameEmbed)

#Checks to see if a user is eligible to be a part of a 
def numGamesPlaying(member):
    count = 0
    for role in member.roles:
        for gameStr in globalvars.GAMES_LIST:
            if gameStr in str(role):
                count = count + 1
    return count

#checks to see if the user that entered the command has permission to
def hasPermission(member):
    for role in member.roles:
        if str(role) in globalvars.EXTRA_PERMS:
            return True
    return False

#determines if a message's content can be turned into an int or not
def isInt(content):
    try:
        int(content)
        return True
    except:
        return False


@client.event
async def on_message(message):
    if message.content == 'shutdown':
        channelName = message.channel.name
        channelSplit = channelName.split('-')
        if len(channelSplit) != 2 or channelSplit[0] not in globalvars.GAMES_LIST or isInt(channelSplit[1]) == False:
            return

        prefix = channelSplit[0]
        number = int(channelSplit[1])

        numslist = []

        if prefix == 'junglevines':
            numslist = globalvars.JUNGLE_NUMS
        elif prefix == 'tag':
            numslist = globalvars.TAG_NUMS
        elif prefix == 'iceslide':
            numslist = globalvars.ICE_SLIDE_NUMS
        elif prefix == 'cannongame':
            numslist = globalvars.CANNON_NUMS
        elif prefix == 'matchminnie':
            numslist = globalvars.MATCH_MINNIE_NUMS
        else:
            return

        await logger.log(f'{str(message.channel)} is shutting down', message.guild)

        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await message.channel.send(embed=embed)
        await asyncio.sleep(2)

        if number in numslist:
            numslist.remove(number)

        guild = message.guild
        for gameStr in globalvars.GAMES_LIST:
            if gameStr in channelName:
                await message.channel.delete()

        
        tag = discord.utils.get(guild.roles, name='tag')
        overrides = message.channel.overwrites
        for overriddenMember in overrides.keys():
            if isinstance(overriddenMember, discord.Member) and tag in overriddenMember.roles:
                await overriddenMember.remove_roles(tag)

        '''
        for role in guild.roles:
            if str(role) == channelName:
                await role.delete()
        '''

    await client.process_commands(message)
client.run(confidential.RUN_ID)