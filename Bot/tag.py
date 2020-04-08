import discord
import random
import asyncio

from timeout import Timeout
import globalvars

class Tag:
    def __init__(self, context, client):
        self.turns = 20
        self.context = context
        self.client = client
        self.players = [context.message.author]
        self.number = self.getChannelNum()
        self.to = Timeout(300)
        self.gameOver = False
        self.numPlayers = 1

    #Creates the channel and gets ready to start the game
    async def createChannel(self):

        #Creating the name using tag-[a number with 4 digits], ex. tag- 0012
        strnum = str(self.number)
        zeroesstrnum = strnum.zfill(4)
        channelRoleName = 'tag-' + zeroesstrnum

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
        await newChannel.send(f'Welcome to Tag, {author.mention}!')  

        #Send message informing the user they need to invite new players
        if self.numPlayers != 2:
            embed = discord.Embed(
                title=str(author),
                description=f'Tag is a two-player game, so you will need to invite someone to this channel! To do that, enter "{globalvars.PREFIX}invite [USER]" to add the user to the channel.\n\nIf you need to leave, enter "shutdown".',
                colour=discord.Color.purple()
            )
            embed.set_footer(text='This channel will delete itself after 5 minutes if nobody has been invited.')
            await newChannel.send(embed=embed)       

        #Wait until the user invites a player or 5 minutes have passed
        while self.numPlayers != 2:
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
                    #Checks to see that the message contains exactly one invite to a user. If so,
                    #the user gets permission to talk in the channel and are sent a ping.
                    mentions = message.mentions
                    if len(mentions) == 1:
                        for member in mentions:
                            #Check to see if the player invites themselves
                            if member == self.players[0]:
                                embed = discord.Embed(
                                    title = "Sorry, you cant really play this game with yourself. :(",
                                    colour = discord.Color.red()
                                )
                                await newChannel.send(embed=embed)
                            else:
                                #adds the player to the game and pings them
                                self.to.resetTimer()
                                self.players.append(member)
                                await member.add_roles(role)
                                await newChannel.set_permissions(member, read_messages = True, send_messages = True)
                                await newChannel.send(f'Welcome to Tag, {member.mention}!')
                                self.numPlayers = self.numPlayers + 1
                    elif len(mentions) == 0:
                        embed = discord.Embed(
                            title = "You must mention another user to invite to the game! Please try again.",
                            colour = discord.Color.red()
                        )
                        await newChannel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title = "You can only add one user to the game! Please try again.",
                            colour = discord.Color.red()
                        )
                        await newChannel.send(embed=embed)
                elif content == 'shutdown':
                    await self.shutdown(newChannel, role)
                else:
                    pass
            
        #These are the players that have not typed start yet
        unreadyPlayers = []
        for player in self.players:
            unreadyPlayers.append(player)
        await newChannel.send(embed=self.startingEmbed())

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
                            unreadyStrs.append(member.mention)
                        unreadyStr = ', '.join(unreadyStrs)
                        await newChannel.send(f'{message.author.mention} is now ready to play Tag. Still waiting on: {unreadyStr}')
                elif content == 'rules':
                    await newChannel.send(embed=self.rulesEmbed())
                elif content == 'shutdown':
                    await self.shutdown(newChannel, role)
                else:
                    pass
        self.to.resetTimer()
        await self.game(newChannel, role)
        pass
        
    #The main game code
    async def game(self, channel, role):
        await channel.send('Made it to the main game code, woop woop!')
        pass

    #Deletes the channel and the role once the minigame is done or the game is manually exited
    async def shutdown(self, channel, role):
        await role.delete()
        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        globalvars.JUNGLE_NUMS.remove(self.number)
        return

    #Gets the random number for the channel
    def getChannelNum(self):
        num = random.randint(1, 9999)
        while (num in globalvars.TAG_NUMS):
            num = random.randint(1, 9999)
        globalvars.TAG_NUMS.append(num)
        return num

    #Returns the embed used at the very beginning before starting the game
    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Tag!',
            description='In order to start the game, both players must type "start" in the chat!\n\nIn order to view rules, type "rules" in the chat!\n\nIf you want to leave, type "shutdown in the chat!',
            colour=discord.Color.green()
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        embed.set_author(name=f'{self.players[0]}, {self.players[1]}')
        return embed

    #Returns the embed for the rules page
    def rulesEmbed(self):
        return

    #Returns the embed for each stage in the game, which differs based on info passed in
    def gameEmbed(self):
        return
    
    #Returns the embed at the end of the game, which differs based on who won
    def endingEmbed(self):
        return
