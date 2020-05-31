import discord
import random
import asyncio

from timeout import Timeout
from junglevines import JungleVines
from tag import Tag
from iceslide import IceSlide
from cannongame import CannonGame
from matchminnie import MatchMinnie
import globalvars
import logger

#Represents a minigame. This is an abstraction of all the individual minigames
#This class creates the channel for the minigame and waits for the game to start,
#then passes the torch onto whatever game the player asked for.
class MiniGame:
    def __init__(self, context, client, prefix, minPlayers, maxPlayers):
        self.context = context
        self.client = client
        self.prefix = prefix
        self.minPlayers = minPlayers
        self.maxPlayers = maxPlayers
        self.players = [context.message.author]
        self.number = 0
        self.to = Timeout(globalvars.SHUTDOWN_TIME)
        self.numslist = []
        self.game = None
        self.numPlayers = 1

    async def createChannel(self):
        #Gets the correct game and list of numbers for the corresponding prefix
        if self.prefix == 'junglevines':
            self.game = JungleVines(self.context, self.client)
            self.numslist = globalvars.JUNGLE_NUMS
        elif self.prefix == 'tag':
            self.game = Tag(self.context, self.client)
            self.numslist = globalvars.TAG_NUMS
        elif self.prefix == 'iceslide':
            self.game = IceSlide(self.context, self.client)
            self.numslist = globalvars.ICE_SLIDE_NUMS
        elif self.prefix == 'cannongame':
            self.game = CannonGame(self.context, self.client)
            self.numslist = globalvars.CANNON_NUMS
        elif self.prefix == 'matchminnie':
            self.game = MatchMinnie(self.context, self.client)
            self.numslist = globalvars.MATCH_MINNIE_NUMS
            
        
        #Gets the number for the game channel and role 
        self.number = self.getChannelNum()

        #Creating the name using junglevines-[a number with 4 digits], ex. junglevines-0123
        strnum = str(self.number)
        zeroesstrnum = strnum.zfill(4)
        channelRoleName = self.prefix + '-' + zeroesstrnum

        guild = self.context.message.guild
        author = self.players[0]

        #First, creating the role that the user will have (role is really only so that they cant
        # make another game when they have it)
        role = await guild.create_role(name=channelRoleName)
        await author.add_roles(role)

        await logger.log(f'new role {channelRoleName} has been created', guild)


        #Next, the channel is made in the category that they sent the message in
        newChannel = await guild.create_text_channel(
            name=channelRoleName,
            category=self.context.message.channel.category
        )
        category = newChannel.category

        await logger.log(f'new channel {channelRoleName} has been created', guild)

        #Then, permissions are set so that the created role can send messages in the channel
        #The rest can read the messages if they want to to see how the game is going
        await newChannel.set_permissions(self.client.user, read_messages = True, send_messages = True)
        await newChannel.set_permissions(guild.default_role, read_messages = False, send_messages = False)
        await newChannel.set_permissions(author, read_messages = True, send_messages = True)
        try:
            spectatorRole = discord.utils.get(guild.roles, name='spectator')
            await newChannel.set_permissions(spectatorRole, read_messages=True, send_messages=False)
        except:
            await logger.log('The spectator role does not exist yet', guild)
    


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
                description=f'This game requires {playersStr} players, so you will need to invite other user(s) to this channel! To do that, enter `{globalvars.PREFIX}invite [USER]` to add the user to the channel.\n\nIf you need to leave, enter `shutdown`.',
                colour=discord.Color.purple()
            )
            embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if nobody has been invited.')
            await newChannel.send(embed=embed)

        #Wait until the user invites a player or 5 minutes have passed
        while self.numPlayers < self.minPlayers:
            if self.to.isTimeUp():
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

                if f'{globalvars.PREFIX}invite' in content:
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
            if self.to.isTimeUp():
                if newChannel in category.channels:
                    await self.shutdown(newChannel, role)
            message = None
            try:
                message = await self.client.wait_for('message', timeout=globalvars.SHUTDOWN_TIME)
            except:
                if newChannel in category.channels:
                    await self.shutdown(newChannel, role)
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
                elif f'{globalvars.PREFIX}invite' in content and self.numPlayers < self.maxPlayers:
                    newUsers = await self.inviteUsers(message, newChannel, role)
                    for user in newUsers:
                        unreadyPlayers.append(user)
                else:
                    pass
        self.to.resetTimer()
        self.game.updateVars(self.players, self.to, self.number)
        await logger.log(f'game sequence for {channelRoleName} has started', guild)
        await self.game.game(newChannel, role)
        pass         

    def getChannelNum(self):
        #Gets the random number for the channel
        num = random.randint(1, 9999)
        numStr = str(num)
        while (num in self.numslist or self.badNumStr(numStr) == True):
            num = random.randint(1, 9999)
        self.numslist.append(num)
        return num
    
    #determines if the 4-digit number contains any part of a bad number
    def badNumStr(self, numStr):
        for badNum in globalvars.BAD_NUMS_AS_STR:
            if badNum in numStr:
                return True
        return False

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
                        title = "Sorry, that player has the noinvites role, meaning that they cannot be invited to multiplayer minigames.",
                        description=f'If this is a mistake, have your friend type `{globalvars.PREFIX}invites` in the minigames commands channel!',
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
                    self.to.resetTimer()
                    self.players.append(member)
                    await member.add_roles(role)
                    await channel.set_permissions(member, read_messages = True, send_messages = True)     
                    await channel.send(f'Welcome, {member.mention}!')
                    self.numPlayers = self.numPlayers + 1
                    newUsers.append(member)
        return newUsers

    #Deletes the channel and the role
    async def shutdown(self, channel, role):
        await role.delete()
        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        self.numslist.remove(self.number)
        return
    
    #Determines if a member is has the noinvites role
    def hasNoInvites(self, member):
        for role in member.roles:
            if str(role) == 'noinvites':
                return False
        return True

    #Checks to see if a user is eligible to be a part of a 
    def numGamesPlaying(self, member):
        count = 0
        for role in member.roles:
            for gameStr in globalvars.GAMES_LIST:
                if gameStr in str(role):
                    count = count + 1
        return count