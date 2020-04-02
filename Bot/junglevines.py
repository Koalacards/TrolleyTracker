import discord
import random
import asyncio

junglenums = []

class JungleVines:
    def __init__(self, context, client):
        self.time = 30
        self.context = context
        self.client = client
        self.author = context.message.author
        self.number = self.getChannelNum()
        self.vines = 8

    async def createChannel(self):
        strnum = str(self.number)
        zeroesstrnum = strnum.zfill(4)
        channelname = 'junglevines-' + zeroesstrnum
        guild = self.context.message.guild
        newChannel = await guild.create_text_channel(
            name=channelname,
            category=self.context.message.channel.category
        )
        await newChannel.send(f'Welcome to Jungle Vines, <@{self.author.id}>!')
        await newChannel.send(embed=self.startingEmbed())
        hasGameStarted = False
        while hasGameStarted == False:
            message = await self.client.wait_for('message', timeout=300)
            if message.channel.id == newChannel.id:
                if message.content == 'start':
                    hasGameStarted = True
                    await self.game(newChannel)
                elif message.content == 'rules':
                    await newChannel.send(embed=self.rulesEmbed())
                elif message.content == None:
                    await newChannel.send('Message has not been recieved, shutting down.')
                else:
                    pass     
        pass

    async def game(self, channel):
        #set up variables
        spider1 = random.randint(2, 4)
        spider2 = random.randint(5, 7)
        currentvine = 1
        currenttime = 0

        await channel.send(embed = self.gameEmbed(False, False, currentvine, currenttime, True, False))

        while currentvine < 8 and currenttime < self.time:
            #the number of seconds the move is going to take: either 1, 2, or 3
            numSeconds = 0
            moveDone = False
            options = ['1', '2', '3']
            #gather the 1, 2, or 3 in the chat
            while moveDone == False:
                message = await self.client.wait_for('message', timeout=300)
                if message.channel.id == channel.id:
                    if message.content in options:
                        numSeconds = int(message.content)
                        if numSeconds > self.time - currenttime:
                            channel.send('You do not have enough time to make this move!')
                            numSeconds = 0
                        else:
                            moveDone = True
                    elif message.content == None:
                        await channel.send('Message has not been recieved, shutting down.')
                    else:
                        pass

            # THE ACTUAL LOGIC BEHIND THE GAME

            #first check to see if numSeconds is legal
            if numSeconds != 1 and numSeconds != 2 and numSeconds != 3:
                await channel.send('Something has gone terribly wrong.')
            
            #The probability that a successful jump will occur. the spider category is the probability
            #that the user is not hit by a spider no matter what option they choose
            probabilities = {
                '1': 50,
                '2': 70,
                '3': 85,
                'spider': 70
            }

            hitBySpider = False
            successfulJump = False

            #first check to see if the user got hit by a spider
            if currentvine == spider1 or currentvine == spider2:
                roll = random.randint(1, 100)
                if roll > probabilities.get('spider'):
                    hitBySpider = True
                    currentvine = currentvine - 1
                    currenttime = currenttime + numSeconds
                
            #now factor in their rolls (unless they got hit by a spider, then the turn is over)
            if hitBySpider == False:
                roll = random.randint(1, 100)
                if roll <= probabilities.get(str(numSeconds)):
                    currentvine = currentvine + 1
                    successfulJump = True
                currenttime = currenttime + numSeconds

            #check for the end of the game
            if currenttime == self.time:
                await channel.send(embed=self.endingEmbed(currenttime, currentvine, False))
                await asyncio.sleep(15)
                await self.shutdown(channel)
                return
                    
            if currentvine == self.vines:
                await channel.send(embed=self.endingEmbed(currenttime, currentvine, True))
                await asyncio.sleep(15)
                await self.shutdown(channel)
                return
            
            
            #check to see if there is a spider on the next vine
            spider = False
            if currentvine == spider1 or currentvine == spider2:
                spider = True
            #if the game is not over, post the message for the next move then redo the loop
            await channel.send(embed=self.gameEmbed(spider=spider, successfulJump=successfulJump, currentvine=currentvine, currenttime=currenttime, firstEmbed=False, spiderHit=hitBySpider))

            #now the while loop starts again for the next turn
        pass

    async def shutdown(self, channel):
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        pass
    
    def getChannelNum(self):
        num = random.randint(1, 9999)
        while (num in junglenums):
            num = random.randint(1, 9999)
        junglenums.append(num)
        return num

    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Jungle Vines!',
            description='In order to start the game, type "start" in the chat!\n\nIn order to view rules, type "rules" in the chat!',
            colour=discord.Color.green()
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        embed.set_author(name=self.author)
        embed.set_image(url='https://vignette.wikia.nocookie.net/toontown/images/f/f0/Jungle_Vines.png/revision/latest/scale-to-width-down/340?cb=20130617235558')
        return embed

    def rulesEmbed(self):
        embed = discord.Embed(
            title='Rules of Junglevines!',
            description='You will have 30 seconds worth of moves to cross 8 vines!\n\nFor every move, you will have the option to take 1, 2, or 3 seconds!\n\nThe less amount of time you use, the lower chance you have of making the jump!\n\nThere will also be spiders on some vines, so be careful and best of luck!\n\nType "start" to begin your expidition!',
            colour=discord.Color.purple()
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        embed.set_author(name=self.author)
        embed.set_image(url='https://vignette.wikia.nocookie.net/toontown/images/f/f0/Jungle_Vines.png/revision/latest/scale-to-width-down/340?cb=20130617235558')
        return embed

    def gameEmbed(self, spider, successfulJump, currentvine, currenttime, firstEmbed, spiderHit):
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
                description = 'A spider hit you off the vine and sent you one vine backwards!'
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
        if spider:
            embed.add_field(name='Be careful!', value='There is a spider on the vine!', inline=False)
        embed.add_field(name='Keep going!', value='Type in "1", "2", or "3" to enter your next jump time!', inline=False)
        embed.add_field(name='1', value='A short but risky jump!', inline=True)
        embed.add_field(name='2', value='A medium-risk jump!', inline=True)
        embed.add_field(name='3', value='A long but very low-risk jump!', inline=True)
        return embed

    def endingEmbed(self, time, vine, win:bool):
        titleStr = ''
        description = ''
        color = None
        if win:
            titleStr = 'Congratulations!'
            description = f'You made it through all 8 vines in {time} seconds. Way to go!'
            color = discord.Color.green()
        else:
            titleStr = 'Nice Try!'
            description = f'Unfortunately, you only made it through {vine} vines in 30 seconds.\nBetter luck next time!'
            color = discord.Color.red()
        embed = discord.Embed(
            title=titleStr,
            description=description,
            colour=color
        )
        embed.set_footer(text='This channel will delete itself in 15 seconds.')
        return embed

