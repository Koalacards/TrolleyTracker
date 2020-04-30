import discord
import globalvars

#help embed for regular players
def regHelpEmbed():
    embed = discord.Embed(
        title='TrolleyTracker Games:',
        description=f'To start any of these games, type `{globalvars.PREFIX}play` and then the name of the game!\nNote that for multiplayer games, you must have server member DM permissions on.',
        colour=discord.Color.purple()
    )
    embed.add_field(name='Single-Player Games:', value='-Jungle Vines\n-Cannon Game', inline=True)
    embed.add_field(name='Multi-Player Games:', value='-Tag (2 players)\n-Ice Slide (2-8 players)', inline=True)
    embed.add_field(name='Other Commands:', value=f'-`{globalvars.PREFIX}noinvites`: Gives you the noinvites role, meaning that other people cant invite you to multiplayer games\n-`{globalvars.PREFIX}invites`: Removes the noinvites role if you have it', inline=False)
    return embed


def modHelpEmbed():
    embed = regHelpEmbed()
    embed.add_field(name='Moderator Commands', value=f'-`{globalvars.PREFIX}resetall`: removes all game channels and roles\n-`{globalvars.PREFIX}reset [Channel Name]`: resets a specific channel and role')
    return embed
