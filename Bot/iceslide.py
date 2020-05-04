import discord
import random
import asyncio
import math
import logger

from timeout import Timeout
import globalvars


#Trolley game of Tag
#-Players: 2-8
#-Requires DM's to be open: yes
#-Length of game: short
#-Description: Game where a random number is generated between a range and people try to guess the
#number, the closer they are the more points they get. There are also barrels and tnt's that can
#add or take away extra points.
class IceSlide:
    def __init__(self, context, client):
        self.rounds = 6
        self.minRange = 5
        self.barrelMultiplier = 5
        self.barrelFreqDivider = 5
        self.bullseyeMultiplier = 5
        self.context = context
        self.client = client
        self.players = [context.message.author]
        self.number = 0
        self.to = Timeout(globalvars.SHUTDOWN_TIME)
        self.color = discord.Color.from_rgb(215, 255, 254)
        self.sleeptime = 15
    
    async def game(self, channel, role):
        roundNum = 1
        currentrange = self.minRange
        points = {}
        for player in self.players:
            points[player] = 0

        #send the first game message
        await channel.send(embed=self.firstGameEmbed(roundNum, points, currentrange))

        #collects dm channels and sends the first DM message to all the players
        dmChannels = []
        for player in self.players:
            if player.dm_channel is None:
                await player.create_dm()
            dmChannels.append(player.dm_channel)
            await player.dm_channel.send(embed=self.dmEmbed(player, currentrange))

        #the full game loop
        while roundNum < self.rounds:
            #declare round-specific variables
            barrelNums = self.genBarrelNums(int(currentrange / 5), currentrange)
            whoGotBarrels = []
            choices = {}
            randomNum = random.randint(1, currentrange)


            #list of players that have not dm'd back a number to the bot
            undecidedPlayers = []
            for player in self.players:
                undecidedPlayers.append(player)

            #Bot looks for numbers in the Dm's or a 'shutdown' in the main iceslide channel
            while len(undecidedPlayers) > 0:
                if self.to.isTimeUp():
                    await self.shutdown(channel, role)
                    return
                message = None
                try:
                    message = await self.client.wait_for('message', timeout=globalvars.SHUTDOWN_TIME)
                except:
                    await self.shutdown(channel, role)
                    return
                if message.channel in dmChannels and message.author in self.players:
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
                        if chosenNum < 1 or chosenNum > currentrange:
                            outOfBoundsEmbed = discord.Embed(
                                title='Whoops!',
                                description=f'Sorry, your not in the range of 1 to {currentrange}. Please try again!',
                                colour=discord.Color.red()
                            )
                            await message.channel.send(embed=outOfBoundsEmbed)
                        else:
                            logger.log(f'{message.author.display_name} has made their move for round {roundNum} in {str(channel)}')
                            await message.channel.send(':thumbsup:')
                            undecidedPlayers.remove(message.author)
                            choices[message.author] = chosenNum
                if message.channel == channel:
                    content = message.content.lower()
                    if content == 'shutdown':
                        await self.shutdown(channel, role)
                        return

            #once all of the numbers have been collected, time to add the points

            pointsGained = {}
            for player, guess in choices.items():
                #points gained from being close to the random number
                calculatedNum = int(max(0, currentrange - math.floor((1.2 * abs(guess - randomNum)))))
                if guess in barrelNums:
                    whoGotBarrels.append(player)
                    #points gained from collecting a barrel
                    addedBarrelPoints = roundNum * self.barrelMultiplier
                    #total points in the round
                    calculatedNum = calculatedNum + addedBarrelPoints
                if guess == randomNum:
                    #points gained from getting a bullseye
                    addedBullseyePoints = roundNum * self.bullseyeMultiplier
                    #total points in the round
                    calculatedNum = calculatedNum + addedBullseyePoints
                #randomness to make it more fun :P
                numPoints = random.randint(calculatedNum, math.floor(1.5 * calculatedNum))
                #add it to the points gained dictionary
                pointsGained[player] = numPoints
                #add it to the overall points dictionary
                points[player] = points[player] + numPoints
            
            #reset variables
            self.to.resetTimer()
            currentrange = currentrange * 2
            roundNum = roundNum + 1
            self.bullseyeMultiplier = currentrange

            #Sends out the embed for the round
            await channel.send(embed=self.gameEmbed(roundNum, points, choices, pointsGained, whoGotBarrels, currentrange, randomNum))

            #send the new dms unless it was the last turn
            if roundNum < self.rounds:
                #wait inbetween sending the embed and the dm
                await asyncio.sleep(self.sleeptime)
                for player in self.players:
                    if player.dm_channel is None:
                        await player.create_dm()
                    await player.dm_channel.send(embed=self.dmEmbed(player, currentrange))
        
        #Once the while is over, determine the winner then do the end embed and shutdown
        #If the length of the winner list is more than one than the result of the game is a tie
        winner = []
        winningNum = 0
        for player in self.players:
            if points[player] > winningNum:
                winner = [player]
                winningNum = points[player]
            elif points[player] == winningNum and len(winner) > 0:
                winner.append(player)

        for winners in winner:
            logger.log(f'{winners.display_name} has won in channel {str(channel)}')
        await channel.send(embed=self.endingEmbed(points, winner))
        await asyncio.sleep(15)
        await self.shutdown(channel, role)
        return

    #Creates a list of numbers that barrels will be collectable at 
    def genBarrelNums(self, amount, currentrange):
        barrelNums = []
        for _ in range(amount):
            num = random.randint(1, currentrange)
            while num in barrelNums:
                num = random.randint(1, currentrange)
            barrelNums.append(num)
        return barrelNums

    #determines if a message's content can be turned into an int or not
    def isInt(self, content):
        try:
            int(content)
            return True
        except:
            return False


    #Deletes the channel and the role once the minigame is done or the game is manually exited
    async def shutdown(self, channel, role):
        logger.log(f'{str(channel)} is shutting down')
        await role.delete()
        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        globalvars.ICE_SLIDE_NUMS.remove(self.number)
        return

    #Starting embed for iceslide
    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Ice Slide!',
            description=f'In order to start the game, all players must enter `start`!\n\nIn order to view rules, enter `rules`!\n\nIf you want to invite more players, enter `{globalvars.PREFIX}invite [USER]`!\n\nIf you want to leave, enter `shutdown`!',
            colour=self.color
            )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if no more players have joined and the game has not started!')
        embed.set_author(name=f'{self.players[0].display_name}')
        return embed
    
    #Rules embed for iceslide
    def rulesEmbed(self):
        embed = discord.Embed(
            title='Rules of Ice Slide!',
            description=f'This game will have {self.rounds} rounds.\n\nFor every round, there will be a randomly generated number between a set range (starts 1-{self.minRange}).\n\nEach person will recieve a DM to guess what the number is.\n\nThe closer you are to the random number, the more points you get!\n\nThe range will increase every round, so hold on tight!\n\nThere will also be random numbers that barrels will spawn on each round, and if you guess one of those numbers you get extra points!\n\nThe person with the most points at the end of the {self.rounds} rounds wins!',
            colour=discord.Color.purple()
            )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if no more players have joined and the game has not started!')
        return embed

    #DM embed for iceslide
    def dmEmbed(self, player, numRange):
        embed = discord.Embed(
            title=f'Ice Slide',
            description=f'{player.display_name}, please enter a number between 1 and {numRange}!',
            colour=self.color
        )
        embed.set_footer(text=f'The iceslide channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a player does not make a move!')
        return embed
    
    #First game embed for iceslide
    def firstGameEmbed(self, startinground, points, currentrange):
        embed = discord.Embed(
            title=f'Round {startinground}/{self.rounds}',
            description='Welcome to Ice Slide and good luck!',
            colour=self.color
        )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a player does not make a move!')
        namesStrs = []
        for player in self.players:
            namesStrs.append(player.display_name)
            embed.add_field(name=f'{player.display_name}', value=f'{points[player]}  points', inline=True)
        embed.add_field(name='Check your DMs!', value=f'You should recieve a message asking for a number between 1 and {currentrange}.', inline=False)
        embed.add_field(name='Keep going!', value='If you would like to exit the game, put `shutdown` in the iceslide channel!', inline=False)
        embed.set_author(name=', '.join(namesStrs))
        return embed

    #Game embed for iceslide
    def gameEmbed(self, roundNum, points, choices, pointsGained, whoGotBarrels, currentrange, randomNum):
        embed = discord.Embed(
            title=f'Round {roundNum}/{self.rounds}',
            description=f'The random number for the last round was: {randomNum}!',
            colour=self.color
        )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a player does not make a move!')
        namesStrs = []
        
        for player in self.players:
            bullseyeStr = ''
            barrelStr=''
            if choices[player] == randomNum:
                bullseyeStr = '-Bullseye!'
            if player in whoGotBarrels:
                barrelStr = '-Barrel Collected!'
            embed.add_field(name=f'{player.display_name}', value=f'Number guessed: {choices[player]}{bullseyeStr}{barrelStr}', inline=True)
        embed.add_field(name='Check your DMs!', value=f'You should recieve a message asking for a number between 1 and {currentrange}.', inline=False)
        for player in self.players:
            pointOrPoints = ''
            if points[player] == 1:
                pointOrPoints = 'point'
            else:
                pointOrPoints = 'points'
            plusPoints = ''
            if points[player] > 0:
                plusPoints = f'(+{pointsGained[player]})'
            namesStrs.append(player.display_name)
            embed.add_field(name=f'{player.display_name}', value=f'{points[player]}  {pointOrPoints} {plusPoints}', inline=True)
        embed.add_field(name='Check your DMs!', value=f'You should recieve a message asking for a number between 1 and {currentrange}.', inline=False)
        embed.add_field(name='Keep going!', value='If you would like to exit the game, put `shutdown` in the iceslide channel!', inline=False)
        embed.set_author(name=', '.join(namesStrs))
        return embed
    
    #Ending embed for iceslide
    def endingEmbed(self, points, winner):
        titles=['Well Done!', 'Way To Go!', 'Awesome!']
        titleStr=titles[random.randint(0, len(titles) - 1)]
        descriptionStr = ''
        color = None
        if len(winner) == 1:
            descriptionStr = f'The winner of this Ice Slide game is {winner[0].display_name}! Congratulations!'
            color = discord.Color.green()
        else:
            winnerStrs = []
            for win in winner:
                winnerStrs.append(win.display_name)
            winnerStr= ','.join(winnerStrs)
            descriptionStr = f'This Ice Slide game is a {len(winner)}-way tie! Congratulations to: {winnerStr}!'
            color = self.color
        embed = discord.Embed(
            title=titleStr,
            description=descriptionStr,
            colour=color
        )
        namesStrs = []
        for player in self.players:
            pointOrPoints = ''
            if points[player] == 1:
                pointOrPoints = 'point'
            else:
                pointOrPoints = 'points'
            namesStrs.append(player.display_name)
            embed.add_field(name=f'{player.display_name}', value=f'{points[player]} {pointOrPoints}', inline=True)
        embed.set_footer(text='This channel will delete itself after 15 seconds.')
        embed.set_author(name=', '.join(namesStrs))
        return embed

    #updates important variables that the minigame script has
    def updateVars(self, players, timeout, number):
        self.players = players
        self.to = timeout
        self.number = number