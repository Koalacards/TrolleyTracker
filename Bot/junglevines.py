import discord
import random

junglenums = []

class JungleVines:
    def __init__(self, context):
        self.time = 30
        self.context = context
        self.number = self.getChannelNum()
        self.vines = 8
        self.currentvine = 1
        self.createChannel()

    async def createChannel(self):
        strnum = str(self.number)
        zeroesstrnum = strnum.zfill(4)
        channelname = 'junglevines-' + zeroesstrnum
        channelID = await self.context.focused_guild.create_text_channel(
            name=channelname,
            reason = 'junglevines game created'
        )
        pass
    
    def getChannelNum(self):
        num = random.randint(1, 9999)
        while (junglenums.__contains__(num)):
            num = random.randint(1, 9999)
        junglenums.__add__(num)
        return num

