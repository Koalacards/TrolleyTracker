import discord
import random
import asyncio

junglenums = []

class JungleVines:
    def __init__(self, context):
        self.time = 30
        self.context = context
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
        await newChannel.send(f'Welcome to junglevines, <@{self.author.id}>!')
        pass
    
    def getChannelNum(self):
        num = random.randint(1, 9999)
        while (num in junglenums):
            num = random.randint(1, 9999)
        junglenums.append(num)
        return num

