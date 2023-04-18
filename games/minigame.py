import discord
from discord.ext import commands
import random
import asyncio

from db.dbfunc import add_game_channel, remove_game_channel
from games.timeout import Timeout
from games.junglevines import JungleVines
from games.tag import Tag
from games.iceslide import IceSlide
from games.cannongame import CannonGame
from games.matchminnie import MatchMinnie
import globalvars
import logger

#Represents a minigame. This is an abstraction of all the individual minigames
#This class creates the channel for the minigame and waits for the game to start,
#then passes the torch onto whatever game the player asked for.
class MiniGame:
    def __init__(self, interaction:discord.Interaction, client: commands.Bot, game_name:str):
        self.interaction = interaction
        self.client = client
        (self.minPlayers, self.maxPlayers) = globalvars.NUM_PLAYERS[game_name]
        self.players = [interaction.user]
        self.game = None
        self.numPlayers = 1
        self.game_name = game_name

    async def createChannel(self):
        guild = self.interaction.guild

        #Gets the correct game and list of numbers for the corresponding prefix
        if self.prefix == 'Jungle Vines':
            self.game = JungleVines(self.interaction, self.client)
        elif self.prefix == 'Tag':
            self.game = Tag(self.interaction, self.client)
        elif self.prefix == 'Ice Slide':
            self.game = IceSlide(self.interaction, self.client)
        elif self.prefix == 'Cannon Game':
            self.game = CannonGame(self.interaction, self.client)
        elif self.prefix == 'Match Minnie':
            self.game = MatchMinnie(self.interaction, self.client)
        else:
            await logger.log("something messed up in the prefix process", self.client)
            return
            
        
        #Gets the number for the game channel and role 
        game_number = str(random.randint(1, 9999))
        zeroesstrnum = game_number.zfill(4)
        channel_name = self.game_name + '-' + zeroesstrnum


        author = self.interaction.user

        overwrites = {
            self.client.user: discord.PermissionOverwrite(read_messages = True, send_messages = True),
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            author: discord.PermissionOverwrite(read_messages = True, send_messages = True)
        }
        #Next, the channel is made in the category that they sent the message in
        newChannel = await guild.create_text_channel(
            name=channel_name,
            category=self.interaction.channel.category,
            overwrites=overwrites
        )
        add_game_channel(newChannel.id)
        to = Timeout(globalvars.SHUTDOWN_TIME, newChannel.id)
        category = newChannel.category

        await logger.log(f'new channel {channel_name} has been created', self.client)

        #Send first message with a ping to direct the user to the channel
        await newChannel.send(f'Welcome, {author.mention}!')

        #Send message informing the user they need to invite new players (if its a multiplayer game)
        if self.minPlayers > 1:
            playersStr = ''
            if self.minPlayers == self.maxPlayers:
                playersStr = str(self.maxPlayers)
            else:
                playersStr = f'{self.minPlayers}-{self.maxPlayers}'
            embed = discord.Embed(
                title=author.display_name,
                description=f'This game requires {playersStr} players, so you will need to invite other user(s) to this channel! To do that, enter `{globalvars.PREFIX}invite [USER MENTION]` to add the user to the channel via mention or `{globalvars.PREFIX}invite name [USER NAME]` to add the user via name.\n\nIf you need to leave, enter `shutdown`.',
                colour=discord.Color.purple()
            )
            embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if nobody has been invited.')
            await newChannel.send(embed=embed)

        #Wait until the user invites a player or 5 minutes have passed
        while self.numPlayers < self.minPlayers:
            if to.isTimeUp():
                if newChannel in category.channels:
                    await self.shutdown(newChannel, role)
                return
            message = None
            try:
                message = await self.client.wait_for('message', timeout=globalvars.SHUTDOWN_TIME)
            except:
                if newChannel in category.channels:
                    await self.shutdown(newChannel, role)
            if message.channel.id == newChannel.id and message.author in self.players:
                content = message.content.lower()

                if f'{globalvars.PREFIX}invite name' in content:
                    newUsers = await self.inviteUsersByName(message, newChannel, role)

                elif f'{globalvars.PREFIX}invite' in content:
                    newUsers = await self.inviteUsers(message, newChannel, role)
                else:
                    pass
                


        #These are the players that have not typed start yet
        unreadyPlayers = []
        for player in self.players:
            unreadyPlayers.append(player)

        #Creates a title for the starting embed containing a concatenation of the players
        startEmbed = self.game.startingEmbed()
        playerstrs = []
        for player in self.players:
            playerstrs.append(player.display_name)
        playerstr = ', '.join(playerstrs)
        startEmbed.set_author(name=playerstr)
        await newChannel.send(embed=startEmbed)  


        #wait until all players have typed start
        while len(unreadyPlayers) > 0:
            if to.isTimeUp():
                if newChannel in category.channels:
                    await self.shutdown(newChannel)
            message = None
            try:
                message = await self.client.wait_for('message', timeout=globalvars.SHUTDOWN_TIME)
            except:
                if newChannel in category.channels:
                    await self.shutdown(newChannel)
            if message.channel.id == newChannel.id and message.author in self.players:
                content = message.content.lower()
                if content == 'start':
                    await logger.log(f'{message.author.display_name} has typed start in {channelRoleName}', guild)
                    if message.author in unreadyPlayers:
                        unreadyPlayers.remove(message.author)
                    
                    if len(unreadyPlayers) > 0:
                        unreadyStrs = []
                        for member in unreadyPlayers:
                            unreadyStrs.append(member.display_name)
                        unreadyStr = ', '.join(unreadyStrs)
                        readyToPlayEmbed= discord.Embed(
                            title=f'{message.author.display_name} is ready to play! Still waiting on: {unreadyStr}',
                            colour=discord.Color.green()
                        )
                        await newChannel.send(embed=readyToPlayEmbed)
                elif content == 'rules':
                    await logger.log(f'{message.author.display_name} has typed rules in {channelRoleName}', guild)
                    await newChannel.send(embed=self.game.rulesEmbed())
                elif f'{globalvars.PREFIX}invite name' in content and self.numPlayers < self.maxPlayers:
                    newUsers = await self.inviteUsersByName(message, newChannel, role)
                    for user in newUsers:
                        unreadyPlayers.append(user)
                elif f'{globalvars.PREFIX}invite' in content and self.numPlayers < self.maxPlayers:
                    newUsers = await self.inviteUsers(message, newChannel, role)
                    for user in newUsers:
                        unreadyPlayers.append(user)
                else:
                    pass
        to.resetTimer()
        self.game.updateVars(self.players, to, self.number)
        await logger.log(f'game sequence for {channelRoleName} has started', guild)
        await self.game.game(newChannel)
        pass         

    #Checks to see that the message contains invites to users (not more than
    #the maximum). If so,
    #the user gets permission to talk in the channel and are sent a ping.
    #This also returns the users that were successfully added to the channel so they
    #can be added to the list of unready players
    async def inviteUsers(self, message, channel, role):
        newUsers = []
        mentions = message.mentions
        if len(mentions) == 0:
            embed = discord.Embed(
                title = "You must mention another user to invite to the game! Please try again.",
                colour = discord.Color.red()
            )
            await channel.send(embed=embed)
        elif len(mentions) + self.numPlayers > self.maxPlayers:
            embed = discord.Embed(
                title = "You tried to add too many people to the game! Please try again.",
                colour = discord.Color.red()
            )
            await channel.send(embed=embed)
        else:
            for member in mentions:
                #Check to see if the player invites themselves
                if member in self.players:
                    embed = discord.Embed(
                        title = "Sorry, you cant play a game with yourself. :(",
                        colour = discord.Color.red()
                    )
                    await channel.send(embed=embed)
                elif self.hasNoInvites(member) == False:
                    embed = discord.Embed(
                        title = f"Player {member.display_name} has the noinvites role, meaning that they cannot be invited to multiplayer minigames.",
                        description=f'If this is a mistake, have them type `{globalvars.PREFIX}invites` in the minigames commands channel!',
                        colour = discord.Color.red()
                    )
                    await channel.send(embed=embed)
                elif self.numGamesPlaying(member) >= globalvars.NUM_GAMES_ALLOWED:
                    inAnotherGameEmbed = discord.Embed(
                        title=f'{member.display_name} is already in {globalvars.NUM_GAMES_ALLOWED} active minigame channel(s)! They must complete their other game(s) before entering this one.',
                        colour=discord.Color.red()
                    )
                    await channel.send(embed=inAnotherGameEmbed)
                else:
                    #adds the player to the game and pings them
                    await logger.log(f'{member.display_name} has been invited to channel {str(channel)}', channel.guild)
                    to.resetTimer()
                    self.players.append(member)
                    await member.add_roles(role)
                    await channel.set_permissions(member, read_messages = True, send_messages = True)     
                    await channel.send(f'Welcome, {member.mention}!')
                    self.numPlayers = self.numPlayers + 1
                    newUsers.append(member)
        return newUsers


    #Same as inviteUsers, except checks by name rather than by mention
    async def inviteUsersByName(self, message, channel, role):
        newUsers = []
        name = message.content.replace('trolley invite name ', '')
        print(name)
        membersFromNames = []
        guild = message.guild
        member = guild.get_member_named(name)
        print(member)
        if member is not None:
            membersFromNames.append(member)
        
        if len(membersFromNames) + self.numPlayers > self.maxPlayers:
            embed = discord.Embed(
                title = "You tried to add too many people to the game! Please try again.",
                colour = discord.Color.red()
            )
            await channel.send(embed=embed)
        else:
            for member in membersFromNames:
                #Check to see if the player invites themselves
                if member in self.players:
                    embed = discord.Embed(
                        title = "Sorry, you cant play a game with yourself. :(",
                        colour = discord.Color.red()
                    )
                    await channel.send(embed=embed)
                elif self.hasNoInvites(member) == False:
                    embed = discord.Embed(
                        title = f"Player {member.display_name} has the noinvites role, meaning that they cannot be invited to multiplayer minigames.",
                        description=f'If this is a mistake, have them type `{globalvars.PREFIX}invites` in the minigames commands channel!',
                        colour = discord.Color.red()
                    )
                    await channel.send(embed=embed)
                elif self.numGamesPlaying(member) >= globalvars.NUM_GAMES_ALLOWED:
                    inAnotherGameEmbed = discord.Embed(
                        title=f'{member.display_name} is already in {globalvars.NUM_GAMES_ALLOWED} active minigame channel(s)! They must complete their other game(s) before entering this one.',
                        colour=discord.Color.red()
                    )
                    await channel.send(embed=inAnotherGameEmbed)
                else:
                    #adds the player to the game and pings them
                    await logger.log(f'{member.display_name} has been invited to channel {str(channel)}', channel.guild)
                    to.resetTimer()
                    self.players.append(member)
                    await member.add_roles(role)
                    await channel.set_permissions(member, read_messages = True, send_messages = True)     
                    await channel.send(f'Welcome, {member.mention}!')
                    self.numPlayers = self.numPlayers + 1
                    newUsers.append(member)
        return newUsers


    #Deletes the channel and the role
    async def shutdown(self, channel: discord.TextChannel):
        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        remove_game_channel(channel.id)

    
    #Determines if a member is has the noinvites role
    def hasNoInvites(self, member):
        for role in member.roles:
            if str(role) == 'noinvites':
                return False
        return True
