import discord
import random
import asyncio

from timeout import Timeout
import globalvars


class JungleVines:
    def __init__(self, context, client):
        self.time = 50
        self.context = context
        self.client = client
        self.author = context.message.author
        self.number = self.getChannelNum()
        self.vines = 15
        self.to = Timeout(300)
        self.gameOver = False

    async def createChannel(self):

        #Creating the name using junglevines-[a number with 4 digits], ex. junglevines-0123
        strnum = str(self.number)
        zeroesstrnum = strnum.zfill(4)
        channelRoleName = 'junglevines-' + zeroesstrnum

        guild = self.context.message.guild

        #First, creating the role that the user will have (role is really only so that they cant
        # make another game when they have it)
        role = await guild.create_role(name=channelRoleName)
        await self.author.add_roles(role)

        #Next, the channel is made in the category that they sent the message in
        newChannel = await guild.create_text_channel(
            name=channelRoleName,
            category=self.context.message.channel.category
        )

        #Then, permissions are set so that the created role can send messages in the channel
        #The rest can read the messages if they want to to see how the game is going
        await newChannel.set_permissions(guild.default_role, read_messages = True, send_messages = False)
        await newChannel.set_permissions(self.author, read_messages = True, send_messages = True)


        #Send first message with a ping to direct the user to the channel
        await newChannel.send(f'Welcome to Jungle Vines, {self.author.mention}!')

        #Send the first embed, describing to type 'rules' or 'start'
        await newChannel.send(embed=self.startingEmbed())

        #Waits for a useful message (either 'rules', 'start', or 'shutdown') and if 
        #the user does not give one in 5 minutes then the channel is shutdown
        hasGameStarted = False
        while hasGameStarted == False and self.gameOver == False:
            if self.to.isTimeUp():
                self.gameOver = True
                await self.shutdown(newChannel, role)
            message = None
            try:
                if self.gameOver == False:
                    message = await self.client.wait_for('message', timeout=300)
            except:
                self.gameOver = True
                await self.shutdown(newChannel, role)
            if message.channel.id == newChannel.id and message.author == self.author:
                content = message.content.lower()
                if content == 'start':
                    self.to.resetTimer()
                    hasGameStarted = True
                    await self.game(newChannel, role)
                elif content == 'rules':
                    await newChannel.send(embed=self.rulesEmbed())
                elif content == 'shutdown':
                    self.gameOver = True
                    await self.shutdown(newChannel, role)
                else:
                    pass     
        pass

    #All of the main game code for junglevines
    async def game(self, newChannel, role):
        #set up variables
        spider1 = random.randint(2, 4)
        bat1 = random.randint(5, 8)
        spider2 = random.randint(9, 11)
        bat2 = random.randint(12, 14)
        currentvine = 1
        currenttime = 0
        totalbananas = 0

        bananas = {}
        for x in range(1, self.vines):
            bananas[x] = random.randint(1, 3)

        batHit = {
           bat1:random.randint(1, 3),
           bat2:random.randint(1, 3) 
        }

        if self.gameOver == False:
            await newChannel.send(embed = self.gameEmbed(False, False, currentvine, currenttime, True, False, False, False, totalbananas, False))

        while currentvine < self.vines and currenttime < self.time and self.gameOver == False:
            #the number of seconds the move is going to take: either 1, 2, or 3
            numSeconds = 0

            #checks for a valid input (either one of the options below or 'shutdown')
            #If there is not a valid input after 5 minutes the channel is shut down
            moveDone = False
            options = ['1', '2', '3']
            
            while moveDone == False and self.gameOver == False:
                if self.to.isTimeUp():
                    self.gameOver = True
                    await self.shutdown(newChannel, role)
                message = None
                try:
                    if self.gameOver == False:
                        message = await self.client.wait_for('message', timeout=300)
                except:
                    self.gameOver = True
                    await self.shutdown(newChannel, role)
                if message.channel.id == newChannel.id and message.author == self.author:
                    content = message.content.lower()
                    if content in options:
                        numSeconds = int(message.content)
                        if numSeconds > self.time - currenttime:
                            await newChannel.send('You do not have enough time to make this move!')
                            numSeconds = 0
                        else:
                            moveDone = True
                            self.to.resetTimer()
                    elif message.content == 'shutdown':
                        self.gameOver = True
                        await self.shutdown(newChannel, role)
                    else:
                        pass

            # THE ACTUAL LOGIC BEHIND THE GAME

            #first check to see if numSeconds is legal
            if numSeconds != 1 and numSeconds != 2 and numSeconds != 3 and self.gameOver == False:
                await newChannel.send('Something has gone terribly wrong.')
            elif self.gameOver == True:
                await asyncio.sleep(15)
                return
            
            #The probability that a successful jump will occur. the spider category is the probability
            #that the user hits a spider and is multiplied for every addition second the user takes
            probabilities = {
                '1': 60,
                '2': 75,
                '3': 85,
                'spider': 15
            }

            hitBySpider = False
            successfulJump = False
            hitByBat = False
            gotBanana = False

            #check to see if the user got a banana
            if bananas[currentvine] == numSeconds:
                totalbananas = totalbananas + 1
                bananas[currentvine] = -1
                gotBanana = True

            #check to see if the user got hit by a spider
            if currentvine == spider1 or currentvine == spider2:
                roll = random.randint(1, 100)
                if roll <= probabilities.get('spider') * numSeconds:
                    hitBySpider = True
                    currentvine = currentvine - 1
                    currenttime = currenttime + numSeconds


            #check to see if the user got hit by a bat
            if currentvine == bat1 or currentvine == bat2:
                if numSeconds == batHit.get(currentvine):
                    hitByBat = True
                    currenttime = currenttime + numSeconds

                
            #now factor in their rolls (unless they got hit by a spider, then the turn is over)
            if hitBySpider == False and hitByBat == False:
                roll = random.randint(1, 100)
                if roll <= probabilities.get(str(numSeconds)):
                    currentvine = currentvine + 1
                    successfulJump = True
                currenttime = currenttime + numSeconds

            #check for the end of the game
            if currentvine == self.vines:
                await newChannel.send(embed=self.endingEmbed(currenttime, currentvine, totalbananas, True))
                await asyncio.sleep(15)
                self.gameOver = True
                await self.shutdown(newChannel, role)
                return

            if currenttime == self.time:
                await newChannel.send(embed=self.endingEmbed(currenttime, currentvine, totalbananas, False))
                await asyncio.sleep(15)
                self.gameOver = True
                await self.shutdown(newChannel, role)
                return
            
            #check to see if there is a spider on the next vine
            spider = False
            if currentvine == spider1 or currentvine == spider2:
                spider = True

            #check to see if there is a bat coming onto the next vine
            bat=False
            if currentvine == bat1 or currentvine == bat2:
                bat=True
            #if the game is not over, post the message for the next move then redo the loop
            await newChannel.send(embed=self.gameEmbed(spider=spider, successfulJump=successfulJump, currentvine=currentvine, currenttime=currenttime, firstEmbed=False, spiderHit=hitBySpider, batHit = hitByBat, gotBanana=gotBanana, bananas=totalbananas, batNow = bat))

            #now the while loop starts again for the next turn
        pass


    #Deletes the channel and the role
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
        while (num in globalvars.JUNGLE_NUMS):
            num = random.randint(1, 9999)
        globalvars.JUNGLE_NUMS.append(num)
        return num

    #The first "welcome to junglevines!" embed information
    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Jungle Vines!',
            description='In order to start the game, type "start" in the chat!\n\nIn order to view rules, type "rules" in the chat!\n\nIf you want to leave, type "shutdown in the chat!',
            colour=discord.Color.green()
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if the game has not started.')
        embed.set_author(name=self.author)
        #embed.set_image(url='https://vignette.wikia.nocookie.net/toontown/images/f/f0/Jungle_Vines.png/revision/latest/scale-to-width-down/340?cb=20130617235558')
        return embed

    #The embed for the rules page
    def rulesEmbed(self):
        embed = discord.Embed(
            title='Rules of Junglevines!',
            description=f'You will have {self.time} seconds worth of moves to cross {self.vines} vines!\n\nFor every move, you will have the option to take 1, 2, or 3 seconds!\n\nThe less amount of time you use, the lower chance you have of making the jump!\n\nThere will also be spiders and bats to avoid!\n\nType "start" to begin your expidition!',
            colour=discord.Color.purple()
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        embed.set_author(name=self.author)
        #embed.set_image(url='https://vignette.wikia.nocookie.net/toontown/images/f/f0/Jungle_Vines.png/revision/latest/scale-to-width-down/340?cb=20130617235558')
        return embed

    #The embed for each message the bot says in the game. This embed is impacted by what has happened
    #in the game.

    #PS:This entire method is hot garbage, talk to @Koalacards#4618 if you need an explanation on something in here
    def gameEmbed(self, spider, successfulJump, currentvine, currenttime, firstEmbed, spiderHit, batHit, gotBanana, bananas, batNow):
        successtitles = ['Awesome!', 'Nice Jump!', 'Woohoo!', 'Way To Go!']
        failtitles = ['Drat!', 'So Close!', 'Better Luck Next Time!', 'Bummer!']
        titleStr = ''
        color = None
        description=''
        if firstEmbed:
            titleStr = 'Begin!'
            description = 'You may start the game, best of luck!'
            color=discord.Color.green()
        else:
            if successfulJump:
                titleStr = successtitles[random.randint(0, len(successtitles) - 1)]
                color=discord.Color.green()
                description = 'Congratulations on a great jump!'
            elif spiderHit:
                titleStr = failtitles[random.randint(0, len(failtitles) - 1)]
                description = 'The spider hit you off the vine and sent you one vine backwards!'
                color=discord.Color.red()
            elif batHit:
                titleStr = failtitles[random.randint(0, len(failtitles) - 1)]
                description = 'The bat hit you off the vine!'
                color=discord.Color.red()
            else: 
                titleStr = failtitles[random.randint(0, len(failtitles) - 1)]
                description = 'You failed to make the jump this time.'
                color=discord.Color.red()
        
        embed = discord.Embed(
            title=titleStr,
            description=description,
            colour=color
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        embed.set_author(name=self.author)
        embed.add_field(name='Time', value=f'{self.time - currenttime}/{self.time}', inline=True)
        embed.add_field(name='Vine', value=f'{currentvine}/{self.vines}', inline=True)
        embed.add_field(name='Total Bananas', value=f'{bananas}', inline=True)
        if gotBanana:
            embed.add_field(name='Congratulations!', value='You got a banana!', inline=False)
            if spider == False and batNow == False:
                embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/635584721232986124/696193848430297118/unknown.png')
        if spider:
            embed.add_field(name='There is a spider on the vine!', value='The longer you stay on the vine, the more likely you are to get hit off!', inline=False)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/697203113425240114/697204990120558673/unknown.png')
        if batNow:
            embed.add_field(name='There is a bat incoming!', value='If you pick the wrong length of time, the bat will knock you off!', inline=False)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/697203113425240114/697204245782331462/unknown.png')
        embed.add_field(name='Keep going!', value='If you would like to exit the game, put "shutdown" in the chat!', inline=False)
        embed.add_field(name='Enter "1":', value='A short but risky jump!', inline=True)
        embed.add_field(name='Enter "2":', value='A medium-risk jump!', inline=True)
        embed.add_field(name='Enter "3":', value='A long but very low-risk jump!', inline=True)
        
        #TODO: add images depending on what happens?
        return embed

    #The embed for when the game is over, either displaying a win or lose message
    def endingEmbed(self, time, vine, bananas, win:bool):
        titleStr = ''
        description = ''
        color = None
        if win:
            titleStr = 'Congratulations!'
            description = f'You made it through all {self.vines} vines in {time} seconds. Way to go!\n\nYou also collected {bananas} bananas.'
            color = discord.Color.green()
        else:
            titleStr = 'Nice Try!'
            description = f'Unfortunately, you only made it through {vine} vines in {self.time} seconds.\nBetter luck next time!\n\nYou also collected {bananas} bananas.'
            color = discord.Color.red()
        embed = discord.Embed(
            title=titleStr,
            description=description,
            colour=color
        )
        embed.set_footer(text='This channel will delete itself in 15 seconds.')
        return embed

