import discord
import random
import asyncio
import math
import logger

from timeout import Timeout
import globalvars

#Trolley game of Match Minnie
#-Players: 2-4
#-Requires DM's to be open: no
#-Length of game: short
#-Description: A random sequence of up, down, left and right is created and added onto every turn.
#Every turn, that sequence will be shown to each player quickly and once the whole sequence is shown,
#the players have to replicate it as fast as possible using wasd keys. Points are given based on
#who is fastest each round.
class MatchMinnie:
    def __init__(self, context, client):
        self.rounds = 4
        self.firstPlacePoints = 10
        self.secondPlacePoints = 7
        self.thirdPlacePoints = 5
        self.fourthPlacePoints = 3
        self.wrongAnswerPoints = 1
        self.context = context
        self.client = client
        self.players = [context.message.author]
        self.number = 0
        self.to = Timeout(globalvars.SHUTDOWN_TIME)
        self.color = discord.Color.from_rgb(244, 143, 177)

    #game code of Match Minnie
    async def game(self, channel, role):
        pass

    #Deletes the channel and the role once the minigame is done or the game is manually exited
    async def shutdown(self, channel, role):
        await logger.log(f'{str(channel)} is shutting down', channel.guild)
        await role.delete()
        embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.delete(reason='removing the game channel because the game is over or was forced to shutdown')
        globalvars.MATCH_MINNIE_NUMS.remove(self.number)
        return

    #starting embed for Match Minnie
    def startingEmbed(self):
        embed = discord.Embed(
            title='Welcome to Match Minnie!',
            description=f'In order to start the game, all players must enter `start`!\n\nIn order to view rules, enter `rules`!\n\nIf you want to invite more players, enter `{globalvars.PREFIX}invite [USER]`!\n\nIf you want to leave, enter `shutdown`!',
            colour=self.color
            )
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if no more players have joined and the game has not started!')
        embed.set_author(name=f'{self.players[0].display_name}')
        return embed

    #rules embed for Match Minnie
    def rulesEmbed(self):
        embed = discord.Embed(
            title='Rules of Match Minnie!',
            description=f'This game will have {self.rounds} rounds.\n\nEvery round, a pattern consisting of up, down, left and right arrows will be played, each arrow lasting for a short amount of time.\n\nEach player will try to replicate the pattern using the "WASD" alternatives!\n\nFor example, to replicate :arrow_up: :arrow_up: :arrow_left:, a user would type `wwd`.\n\nThe faster you replicate the pattern compared to your peers, the more points you get!',
            colour=discord.Color.purple()
            )
        embed.add_field(name='How the points are calculated:', value=f'First place gets {self.firstPlacePoints}, second place gets {self.secondPlacePoints}, third place gets {self.thirdPlacePoints} (if applicable), and fourth place gets {self.fourthPlacePoints} (if applicable). Wrong answers get {self.wrongAnswerPoints} points.', inline=False)
        embed.set_footer(text=f'This channel will delete itself after {globalvars.SHUTDOWN_TIME_MINS} minutes if no more players have joined and the game has not started!')
        return embed

    #the first game embed for Match Minnie
    def firstGameEmbed(self):
        embed = discord.Embed(
            title='hi'
        )
        return embed
    
    #The game embed for Match Minnie
    def gameEmbed(self):
        embed= discord.Embed(
            title='hi'
        )
        return embed

    #updates important variables that the minigame script has
    def updateVars(self, players, timeout, number):
        self.players = players
        self.to = timeout
        self.number = number