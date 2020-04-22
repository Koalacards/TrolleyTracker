import discord
import random
import asyncio

from timeout import Timeout
from junglevines import JungleVines
from tag import Tag
import globalvars

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
        self.to = Timeout(300)
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
            pass
        
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

        #Next, the channel is made in the category that they sent the message in
        newChannel = await guild.create_text_channel(
            name=channelRoleName,
            category=self.context.message.channel.category
        )

        #Then, permissions are set so that the created role can send messages in the channel
        #The rest can read the messages if they want to to see how the game is going
        await newChannel.set_permissions(guild.default_role, read_messages = True, send_messages = False)
        await newChannel.set_permissions(author, read_messages = True, send_messages = True)

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
                description=f'This game requires {playersStr} players, so you will need to invite other user(s) to this channel! To do that, enter "{globalvars.PREFIX}invite [USER]" to add the user to the channel.\n\nIf you need to leave, enter "shutdown".',
                colour=discord.Color.purple()
            )
            embed.set_footer(text='This channel will delete itself after 5 minutes if nobody has been invited.')
            await newChannel.send(embed=embed)

        #Wait until the user invites a player or 5 minutes have passed
        while self.numPlayers < self.minPlayers:
            if self.to.isTimeUp():
                await self.shutdown(newChannel, role)
                return
            message = None
            try:
                message = await self.client.wait_for('message', timeout=300)
            except:
                await self.shutdown(newChannel, role)
            if message.channel.id == newChannel.id and message.author in self.players:
                content = message.content.lower()

                if f'{globalvars.PREFIX}invite' in content:
                    #Checks to see that the message contains invites to users (not more than
                    #the maximum). If so,
                    #the user gets permission to talk in the channel and are sent a ping.
                    mentions = message.mentions
                    if len(mentions) == 0:
                        embed = discord.Embed(
                            title = "You must mention another user to invite to the game! Please try again.",
                            colour = discord.Color.red()
                        )
                        await newChannel.send(embed=embed)
                    elif len(mentions) + self.numPlayers > self.maxPlayers:
                        embed = discord.Embed(
                            title = "You tried to add too many people to the game! Please try again.",
                            colour = discord.Color.red()
                        )
                        await newChannel.send(embed=embed)
                    else:
                        for member in mentions:
                            #Check to see if the player invites themselves
                            if member == self.players[0]:
                                embed = discord.Embed(
                                    title = "Sorry, you cant play a game with yourself. :(",
                                    colour = discord.Color.red()
                                )
                                await newChannel.send(embed=embed)
                            else:
                                #adds the player to the game and pings them
                                self.to.resetTimer()
                                self.players.append(member)
                                await member.add_roles(role)
                                await newChannel.set_permissions(member, read_messages = True, send_messages = True)
                                await newChannel.send(f'Welcome, {member.mention}!')
                                self.numPlayers = self.numPlayers + 1
                elif content == 'shutdown':
                    await self.shutdown(newChannel, role)
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
                await self.shutdown(newChannel, role)
            message = None
            try:
                message = await self.client.wait_for('message', timeout=300)
            except:
                await self.shutdown(newChannel, role)
            if message.channel.id == newChannel.id and message.author in self.players:
                content = message.content.lower()
                if content == 'start':
                    if message.author in unreadyPlayers:
                        unreadyPlayers.remove(message.author)
                    
                    if len(unreadyPlayers) > 0:
                        unreadyStrs = []
                        for member in unreadyPlayers:
                            unreadyStrs.append(member.display_name)
                        unreadyStr = ', '.join(unreadyStrs)
                        await newChannel.send(f'{message.author.display_name} is ready to play! Still waiting on: {unreadyStr}')
                elif content == 'rules':
                    await newChannel.send(embed=self.game.rulesEmbed())
                elif content == 'shutdown':
                    await self.shutdown(newChannel, role)
                elif f'{globalvars.PREFIX}invite' in content and self.numPlayers < self.maxPlayers:
                    mentions = message.mentions
                    if len(mentions) == 0:
                        embed = discord.Embed(
                            title = "You must mention another user to invite to the game! Please try again.",
                            colour = discord.Color.red()
                        )
                        await newChannel.send(embed=embed)
                    elif len(mentions) + self.numPlayers > self.maxPlayers:
                        embed = discord.Embed(
                            title = "You tried to add too many people to the game! Please try again.",
                            colour = discord.Color.red()
                        )
                        await newChannel.send(embed=embed)
                    else:
                        for member in mentions:
                            #Check to see if the player invites themselves
                            if member == self.players[0]:
                                embed = discord.Embed(
                                    title = "Sorry, you cant play a game with yourself. :(",
                                    colour = discord.Color.red()
                                )
                                await newChannel.send(embed=embed)
                            else:
                                #adds the player to the game and pings them
                                self.to.resetTimer()
                                self.players.append(member)
                                await member.add_roles(role)
                                await newChannel.set_permissions(member, read_messages = True, send_messages = True)
                                await newChannel.send(f'Welcome, {member.mention}!')
                                self.numPlayers = self.numPlayers + 1
                                unreadyPlayers.append(member)
                else:
                    pass
        self.to.resetTimer()
        self.game.updateVars(self.players, self.to, self.number)
        await self.game.game(newChannel, role)
        pass         

        pass

    def getChannelNum(self):
        #Gets the random number for the channel
        num = random.randint(1, 9999)
        while (num in self.numslist):
            num = random.randint(1, 9999)
        self.numslist.append(num)
        return num

    #Deletes the channel and the role
    async def shutdown(self, channel, role):
        await role.delete()
        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        self.numslist.remove(self.number)
        return