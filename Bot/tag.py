import discord
import random
import asyncio

from timeout import Timeout
import globalvars

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
        self.maxRange = 20
        self.context = context
        self.client = client
        self.players = [context.message.author]
        self.number = 0
        self.to = Timeout(300)
        
    #The main game code
    async def game(self, channel, role):
        #set up the variables
        cones = {}
        for player in self.players:
            cones[player] = 0
        numRange = self.maxRange
        turn = 1
        playerIt = self.players[random.randint(0, len(self.players) - 1)]

        #first game embed, the rest of the embeds will be generated in gameEmbed
        firstGameEmbed = discord.Embed(
            title='Begin!',
            description=f'It has been determined... {playerIt.display_name} is IT!',
            colour=discord.Color.orange()
        )
        firstGameEmbed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        namesStrs = []
        firstGameEmbed.add_field(name='Turn', value=f'{turn}/{self.turns}', inline=True)
        for player in self.players:
            namesStrs.append(player.display_name)
            firstGameEmbed.add_field(name=f'{player.display_name}', value=f'{cones[player]} cones', inline=True)
        firstGameEmbed.add_field(name='Check your DMs!', value=f'You should recieve a message asking for a number between 1 and {numRange}.', inline=False)
        firstGameEmbed.add_field(name='Keep going!', value='If you would like to exit the game, put "shutdown" in the chat!', inline=False)
        firstGameEmbed.set_author(name=', '.join(namesStrs))
        await channel.send(embed=firstGameEmbed)

        #sends the first DM to each user and creates a list of the dm channels for later
        dmChannels=[]
        for player in self.players:
            if player.dm_channel is None:
                await player.create_dm()
            dmChannels.append(player.dm_channel)
            await player.dm_channel.send(embed=self.dmEmbed(player, numRange))
        

        #The full game loop
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

    #Returns the embed used at the very beginning before starting the game
    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Tag!',
            description='In order to start the game, both players must type "start" in the chat!\n\nIn order to view rules, type "rules" in the chat!\n\nIf you want to leave, type "shutdown in the chat!',
            colour=discord.Color.orange()
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        embed.set_author(name=f'{self.players[0].display_name}')
        return embed

    #Returns the embed for the rules page
    def rulesEmbed(self):
        embed = discord.Embed(
            title='Rules of Tag!',
            description=f'This game will have {self.turns} turns.\n\nFor every turn, each player will recieve a DM to guess a number between a given range (starts 1-20).\n\nIf the two players guess the same number, the other player becomes it!\n\nIf they do not, the person who is not it gains ice cream cones and the range shrinks for the next turn.\n\nThe person with the most ice cream cones after all of the turns wins!',
            colour=discord.Color.purple()
            )
        embed.set_footer(text='This channel will delete itself after 5 minutes if no action is taken!')
        return embed

    #Returns the embed for the message that is DM'd to each user
    def dmEmbed(self, player, numrange):
        embed = discord.Embed(
            title=f'Tag',
            description=f'{player.display_name}, please enter a number between 1 and {numrange}!',
            colour=discord.Color.orange()
        )
        embed.set_footer(text='The tag channel will delete itself after 5 minutes if no action is taken!')
        return embed

    #Returns the embed for each stage in the game, which differs based on info passed in
    def gameEmbed(self, cones, playerIt, turn):
        return
    
    #Returns the embed at the end of the game, which differs based on who won
    def endingEmbed(self):
        return

    def updateVars(self, players, timeout, number):
        self.players = players
        self.to = timeout
        self.number = number
