import discord
import random
import asyncio

from timeout import Timeout
import globalvars
import logger

#Trolley game of Tag
#-Players: 2
#-Requires DM's to be open: yes
#-Length of game: short
#-Description: Fun game with a friend where you guess a number in a range, and if both of you
#guess the same number, the other person becomes IT. The range gets smaller every turn that passes
#where the two people guess different numbers, and the smaller the range, the more icecream cones
#the player that is not IT gets.
class Tag:
    def __init__(self, context, client):
        self.turns = 20
        self.maxRange = 16
        self.context = context
        self.client = client
        self.players = [context.message.author]
        self.number = 0
        self.to = Timeout(globalvars.SHUTDOWN_TIME)
        self.color = discord.Color.from_rgb(201, 167, 152)
        self.sleeptime = 5
        
    #The main game code
    async def game(self, channel, role):
        #set up the variables
        cones = {}
        for player in self.players:
            cones[player] = 0
        numRange = self.maxRange
        turn = 0
        playerIt = self.players[random.randint(0, len(self.players) - 1)]
        category = channel.category

        #first game embed, the rest of the embeds will be generated in gameEmbed
        firstGameEmbed = discord.Embed(
            title=f'Turn {turn}/{self.turns}',
            description=f'It has been determined... {playerIt.display_name} is IT!',
            colour=self.color
        )
        firstGameEmbed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a player has not made a move!')
        namesStrs = []
        for player in self.players:
            namesStrs.append(player.display_name)
            firstGameEmbed.add_field(name=f'{player.display_name}', value=f'{cones[player]}  ice cream cones', inline=True)
        firstGameEmbed.add_field(name='Check your DMs!', value=f'You should recieve a message asking for a number between 1 and {numRange}.', inline=False)
        firstGameEmbed.add_field(name='Keep going!', value='If you would like to exit the game, put `shutdown` in the tag channel!', inline=False)
        firstGameEmbed.set_author(name=', '.join(namesStrs))
        await channel.send(embed=firstGameEmbed)

        #sends the first DM to each user
        for player in self.players:
            if player.dm_channel is None:
                await player.create_dm()
            await player.dm_channel.send(embed=self.dmEmbed(player, numRange))
        

        #The full game loop
        for _ in range(self.turns):
            #the number each person picks in each turn
            choices = {}

            #creates a client wait-for system with each player to grab the message for their next move
            undecidedPlayers = []
            for player in self.players:
                undecidedPlayers.append(self.getMessage(player, channel, category, role, numRange, turn))
            
            #grabbing the messages from players
            try:   
                done, tasks = await  asyncio.wait(undecidedPlayers, return_when=asyncio.ALL_COMPLETED)
                if len(tasks):
                    if channel in category.channels:
                        await self.shutdown(channel, role)
                    return
                for task in done:
                    result = task.result()
                    if result is None:
                        return
                    else:
                        chosenNumber = result[0]
                        player = result[1]
                        choices[player] = chosenNumber
            except:
                if channel in category.channels:
                    await self.shutdown(channel, role)
                return
            
            #now that all players have decided, reset the timer and go onto the logic of the game
            self.to.resetTimer()
            turn = turn + 1
            sameGuess = True
            
            #GAME LOGIC

            #First check to see if the numbers are the same
            firstnum = choices[self.players[0]]
            for player in self.players:
                if choices[player] != firstnum:
                    sameGuess = False
            
            conesGained = {}
            if sameGuess == True:
                #switch up the playerIT
                for player in self.players:
                    if player != playerIt:
                        playerIt = player
                        break
                
                #reset vars
                numRange = self.maxRange
                #send the embed
                roundMessage = await channel.send(embed=self.gameEmbed(cones, playerIt, turn, choices, conesGained, True, numRange))
                for player in self.players:
                    if player.dm_channel is None:
                        await player.create_dm()
                    await player.dm_channel.send(f'Last round\'s results: {roundMessage.jump_url}')
            else:
                #find the player that is not it
                playerNotIt = None
                for player in self.players:
                    if player != playerIt:
                        playerNotIt = player
                
                #establish the number of ice cream cones gained by the player
                numGained = random.randint(int(self.maxRange / numRange), 2 * int(self.maxRange / numRange))
                conesGained[playerNotIt] = numGained
                cones[playerNotIt] = cones[playerNotIt] + numGained

                #half the range
                numRange = int(numRange / 2)

                #this round's message if the roles are not switched
                roundMessage = await channel.send(embed=self.gameEmbed(cones, playerIt, turn, choices, conesGained, False, numRange))
                for player in self.players:
                    if player.dm_channel is None:
                        await player.create_dm()
                    await player.dm_channel.send(f'Last round\'s results: {roundMessage.jump_url}')


            #send the new dms unless it was the last turn
            if turn < self.turns:
                #wait inbetween sending the embed and the dm
                await asyncio.sleep(self.sleeptime)
                for player in self.players:
                    if player.dm_channel is None:
                        await player.create_dm()
                    await player.dm_channel.send(embed=self.dmEmbed(player, numRange))
        
        #after the last turn determine the winner, do the end embed then shutdown
        winner = None
        winningNum = 0
        for player in self.players:
            if cones[player] > winningNum:
                winner = player
                winningNum = cones[player]
            elif cones[player] == winningNum and winner is not None:
                winner = None
        await channel.send(embed=self.endingEmbed(cones, winner))
        await asyncio.sleep(globalvars.END_COOLDOWN_TIME)
        await self.shutdown(channel, role)
        return

    #Gets a message from one of the players in the game
    async def getMessage(self, player, channel, category, role, numRange, turn):
        while(True):
            if self.to.isTimeUp():
                if channel in category.channels:
                    await self.shutdown(channel, role)
                return None
            message = None
            try:
                 message = await self.client.wait_for('message', timeout=globalvars.SHUTDOWN_TIME)
            except:
                if channel in category.channels:
                    await self.shutdown(channel, role)
                return None
            if message.author == player and message.channel == player.dm_channel:
                content = message.content.lower()
                if self.isInt(content) == False:
                    failedNumEmbed = discord.Embed(
                        title='Whoops!',
                        description='Sorry, your answer was not a number. Please try again!',
                        colour=discord.Color.red()
                    )
                    await message.channel.send(embed=failedNumEmbed)
                else:
                    chosenNum = int(content)
                    #now that the message is definitely a number, determine if its between the targets
                    if chosenNum < 1 or chosenNum > numRange:
                        outOfBoundsEmbed = discord.Embed(
                                title='Whoops!',
                                description=f'Sorry, your not in the range of 1 to {numRange}. Please try again!',
                                colour=discord.Color.red()
                            )
                        await message.channel.send(embed=outOfBoundsEmbed)
                    else:
                        await logger.log(f'{message.author.display_name} has made their move for turn {turn} in {str(channel)}', channel.guild)
                        await message.channel.send(':thumbsup:')
                        return [chosenNum, player]

    #Deletes the channel and the role once the minigame is done or the game is manually exited
    async def shutdown(self, channel, role):
        await logger.log(f'{str(channel)} is shutting down', channel.guild)
        await role.delete()
        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        globalvars.TAG_NUMS.remove(self.number)
        return

    #Returns the embed used at the very beginning before starting the game
    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Tag!',
            description='In order to start the game, both players must enter `start`!\n\nIn order to view rules, enter `rules`!\n\nIf you want to leave, enter `shutdown`!',
            colour=self.color
            )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if the game has not started!')
        embed.set_author(name=f'{self.players[0].display_name}')
        return embed

    #Returns the embed for the rules page
    def rulesEmbed(self):
        embed = discord.Embed(
            title='Rules of Tag!',
            description=f'This game will have {self.turns} turns.\n\nFor every turn, each player will recieve a DM to guess a number between a given range (starts 1-{self.maxRange}).\n\nIf the two players guess the same number, the other player becomes it!\n\nIf they do not, the person who is not it gains ice cream cones and the range shrinks for the next turn.\n\nThe person with the most ice cream cones after all of the turns wins!',
            colour=discord.Color.purple()
            )
        embed.add_field(name=f'How the icecream cones are calculated:', value=f'When you are not it, you get a random number of cones between the range [{self.maxRange}/(the largest number in the current range)] to 2 * [{self.maxRange}/(the largest number in the current range)]', inline=False)
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if the game has not started!')
        return embed

    #Returns the embed for the message that is DM'd to each user
    def dmEmbed(self, player, numrange):
        embed = discord.Embed(
            title=f'Tag',
            description=f'{player.display_name}, please enter a number between 1 and {numrange}!',
            colour=self.color
        )
        embed.set_footer(text=f'The tag channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a player does not make a move!')
        return embed

    #Returns the embed for each stage in the game, which differs based on info passed in
    def gameEmbed(self, cones, playerIt, turn, choices, whoGainedCones, switch, numRange):
        titlestr = f'Turn {turn}/{self.turns}'
        descriptionstr=''
        color = self.color
        if switch == True:
            descriptionstr = f'{playerIt.display_name} is now IT!'
            color=discord.Color.teal()
        else:
            descriptionstr = f'{playerIt.display_name} is still IT!'
        embed = discord.Embed(
            title=titlestr,
            description=descriptionstr,
            colour=color
        )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a player does not make a move!')
        namesStrs = []
        for player in self.players:
            embed.add_field(name=f'{player.display_name}', value=f'Number was: {choices[player]}', inline=True)
        embed.add_field(name='Check your DMs!', value=f'You should recieve a message asking for a number between 1 and {numRange}.', inline=False)
        for player in self.players:
            plusCones = ''
            if player in whoGainedCones.keys():
                plusCones = f'(+{whoGainedCones[player]})'
            coneOrCones = ''
            if cones[player] == 1:
                coneOrCones = 'cone'
            else:
                coneOrCones = 'cones'
            namesStrs.append(player.display_name)
            embed.add_field(name=f'{player.display_name}', value=f'{cones[player]} ice cream {coneOrCones} {plusCones}', inline=True)
        embed.add_field(name='Keep going!', value='If you would like to exit the game, put `shutdown` in the tag channel!', inline=False)
        embed.set_author(name=', '.join(namesStrs))
        return embed
    
    #Returns the embed at the end of the game, which differs based on who won
    def endingEmbed(self, cones, winner):
        titles=['Well Done!', 'Way To Go!', 'Awesome!']
        titleStr=titles[random.randint(0, len(titles) - 1)]
        descriptionStr = ''
        color = None
        if winner is None:
            descriptionStr = 'The outcome of this Tag game is a tie! Well done to both players!'
            color = self.color
        else:
            descriptionStr = f'The winner of this Tag game is {winner.display_name}! Congratulations!'
            color = discord.Color.green()
        embed = discord.Embed(
            title = titleStr,
            description= descriptionStr,
            colour=color
        )
        namesStrs = []
        for player in self.players:
            coneOrCones = ''
            if cones[player] == 1:
                coneOrCones = 'cone'
            else:
                coneOrCones = 'cones'
            namesStrs.append(player.display_name)
            embed.add_field(name=f'{player.display_name}', value=f'{cones[player]} ice cream {coneOrCones}', inline=True)
        embed.set_footer(text=f'This channel will delete itself in {globalvars.END_COOLDOWN_TIME} seconds.')
        embed.set_author(name=', '.join(namesStrs))
        return embed

    def updateVars(self, players, timeout, number):
        self.players = players
        self.to = timeout
        self.number = number

    def isInt(self, content):
        try:
            int(content)
            return True
        except:
            return False
