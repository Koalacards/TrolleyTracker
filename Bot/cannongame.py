import discord
import random
import asyncio

from timeout import Timeout
import globalvars
import logger

#Trolley game of CannonGame
#-Players: 1
#-Requires DM's to be open: no
#-Length of game: short
#-Description: In a 1000x1000 range you have to guess two numbers that are within two randomly
#generated 10-wide ranges.
class CannonGame:
    def __init__(self, context, client):
        self.range = 1000
        self.context=context
        self.client=client
        self.xMin = random.randint(1, self.range - 10)
        self.xMax = self.xMin + 10
        self.yMin = random.randint(1, self.range - 10)
        self.yMax = self.yMin + 10
        self.author = context.message.author
        self.to = Timeout(globalvars.SHUTDOWN_TIME)
        self.color = discord.Color.from_rgb(58, 196, 250)
        self.number = 0

    #game part of cannongame
    async def game(self, channel, role):
        #variables needed
        attempt = 1
        gameOver = False
        category = channel.category

        #send the first embed
        await channel.send(embed=self.firstGameEmbed())


        #while loop for the game
        while(gameOver == False):

            hasGuessed = False
            xGuess = None
            yGuess = None

            #First get the numbers
            while(hasGuessed == False):
                if self.to.isTimeUp():
                    if channel in category.channels:
                        await self.shutdown(channel, role)
                    return
                message = None
                try:
                    message = await self.client.wait_for('message', timeout=globalvars.SHUTDOWN_TIME)
                except:
                    if channel in category.channels:
                        await self.shutdown(channel, role)
                    return
                if message.channel.id == channel.id and message.author == self.author:
                    content = message.content.lower()
                    contentSplit = content.split()
                    if len(contentSplit) == 2:
                        validNums = True
                        for content in contentSplit:
                            if self.isInt(content) == False:
                                failedNumEmbed = discord.Embed(
                                title='Whoops!',
                                description='Sorry, one of your answers was not a number. Please try again!',
                                colour=discord.Color.red()
                                )
                                await message.channel.send(embed=failedNumEmbed)
                                validNums = False
                        
                        if validNums == True:
                            xGuess = int(contentSplit[0])
                            yGuess = int(contentSplit[1])

                            if xGuess < 1 or xGuess > self.range or yGuess < 1 or yGuess > self.range:
                                xGuess = None
                                yGuess = None
                                notInRangeEmbed = discord.Embed(
                                title='Whoops!',
                                description=f'Sorry, one of your numbers was out of the range of 1 to {self.range}. Please try again!',
                                colour=discord.Color.red()
                                )
                                await message.channel.send(embed=notInRangeEmbed)
                            else:
                                logger.log(f'{self.author.display_name} has entered a guess for attempt {attempt}  in {str(channel)}')
                                hasGuessed = True

                    elif content == 'shutdown':
                        await self.shutdown(channel, role)
                        return
            
            self.to.resetTimer()
            
            #Check to see if the game is over, if not move to the next turn
            if xGuess >= self.xMin and xGuess <= self.xMax and yGuess >= self.yMin and yGuess <= self.yMax:
                logger.log(f'{self.author.display_name} has won cannongame in {str(channel)}')
                await channel.send(embed=self.endingEmbed(attempt, xGuess, yGuess))
                await asyncio.sleep(15)
                await self.shutdown(channel, role)
                gameOver = True
                return
            
            #If the game is not over, send the next message and move on
            attempt = attempt + 1
            await channel.send(embed=self.gameEmbed(attempt, xGuess, yGuess))
               
        return



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
        globalvars.CANNON_NUMS.remove(self.number)
        return
    
    #starting embed for cannon game
    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Cannon Game!',
            description='In order to start the game, enter `start`!\n\nIn order to view rules, enter `rules`!\n\nIf you want to leave, enter `shutdown`!',
            colour=self.color
            )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if the game has not started.')
        embed.set_author(name=self.author.display_name)
        return embed
    
    #rules embed for cannon game
    def rulesEmbed(self):
        embed = discord.Embed(
            title='Rules of Cannon Game!',
            description=f'You will have an unlimited amount of tries to guess the correct coordinates of the water bucket!\n\nThe grid is 1000x1000, so for every guess you will put in two numbers between 1 and 1000, one for the horizontal coordinate and one for the vertical.\n\nAn example of a proper guess is `10 10`.\n\nOnce you guess a correct coordinate, the game is over and you win!\n\nTry to land a splash in as few turns as you can!',
            colour=discord.Color.purple()
            )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if the game has not started.')
        return embed

    #first game embed for cannon game
    def firstGameEmbed(self):
        x = random.randint(1, 1000)
        y = random.randint(1, 1000)
        embed = discord.Embed(
            title='Attempt 1',
            description=f'Enter an attempt by typing in two numbers between 1 and 1000 separated by a space!\nExample guess: `{x} {y}`',
            colour = self.color
        )
        embed.add_field(name='Keep going!', value='If you would like to exit the game, enter `shutdown`!', inline=False)
        embed.set_author(name=self.author.display_name)
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a move has not been made.')
        return embed

    #game embed for cannon game
    def gameEmbed(self, attempt, xguess, yguess):
        x = random.randint(1, 1000)
        y = random.randint(1, 1000)
        xStr = ''
        if xguess < self.xMin:
            xStr = 'too low'
        elif xguess > self.xMax:
            xStr = 'too high'
        else:
            xStr = 'in the range'
        yStr = ''
        if yguess < self.yMin:
            yStr = 'too low'
        elif yguess > self.yMax:
            yStr = 'too high'
        else:
            yStr = 'in the range'
        embed = discord.Embed(
            title=f'Attempt {attempt}',
            description=f'Enter an attempt by typing in two numbers between 1 and 1000 separated by a space!\nExample guess: `{x} {y}`',
            colour = self.color
        )
        embed.add_field(name='Guesses', value=f'Your horizontal guess of {xguess} (your first number) was {xStr}.\nYour vertical guess of {yguess} (your second number) was {yStr}.')
        embed.add_field(name='Keep going!', value='If you would like to exit the game, enter `shutdown`!', inline=False)
        embed.set_author(name=self.author.display_name)
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if a move has not been made.')
        return embed
    
    #ending embed for cannon game
    def endingEmbed(self, attempt, xguess, yguess):
        embed = discord.Embed(
            title='Congratulations!',
            description=f'You found the bucket of water in {attempt} attempts!',
            colour=discord.Color.green()
        )
        embed.add_field(name='Your final numbers:', value=f'Horizontal: {xguess}\nVertical: {yguess}', inline=False)
        embed.add_field(name='The bucket horizontal and vertical ranges:', value=f'Horizontal: {self.xMin} to {self.xMax}\nVertical: {self.yMin} to {self.yMax}', inline=False)
        embed.set_footer(text='This channel will delete itself in 15 seconds.')
        return embed


    def updateVars(self, players, timeout, number):
        self.author = players[0]
        self.to = timeout
        self.number = number
    