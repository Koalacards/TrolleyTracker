import discord
import random

junglenums = []

class JungleVines:
    def __init__(self, context, client):
        self.time = 30
        self.context = context
        self.client = client
        self.author = context.message.author
        self.number = self.getChannelNum()
        self.vines = 8
        self.currentvine = 1

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
                    await newChannel.send('starting')
                    hasGameStarted = True
                    await self.game()
                elif message.content == 'rules':
                    await newChannel.send(embed=self.rulesEmbed())
                elif message.content == None:
                    await newChannel.send('Message has not been recieved, shutting down.')
                else:
                    pass     
        pass

    async def game(self):
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

    def gameEmbed(self):
        pass

    def endingEmbed(self):
        pass

