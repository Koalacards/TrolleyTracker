import discord
import globalvars

#help embed for regular players
def regHelpEmbed():
    embed = discord.Embed(
        title='TrolleyTracker Help Page',
        description=f'To start a game, type `{globalvars.PREFIX}play` and then the name of the game!\nNote that for multiplayer games, you must have server member DM permissions on.',
        colour=discord.Color.purple()
    )
    embed.add_field(name='Single-Player Games:', value='-Jungle Vines\n-Cannon Game', inline=True)
    embed.add_field(name='Multi-Player Games:', value='-Tag (2 players)\n-Ice Slide (2-8 players)', inline=True)
    embed.add_field(name='Other Commands:', value=f'-`{globalvars.PREFIX}suggest [message]`: Put any suggestion you have for the bot in here and it will be recorded!', inline=False)
    return embed


def modHelpEmbed():
    embed = regHelpEmbed()
    embed.add_field(name='Moderator Commands', value=f'-`{globalvars.PREFIX}resetall`: removes all game channels and roles\n-`{globalvars.PREFIX}reset [Channel Name]`: resets a specific channel and role')
    return embed
