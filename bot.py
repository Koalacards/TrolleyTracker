import discord
from discord.ext import commands, tasks

from confidential import RUN_ID

'''
TODO:Functionality that should be added:
    -a check that each user has DM's open before playing any game that involves DM's
        -an alternate way of doing this is making the channels non-read for players who arent inputting to the game
    
'''
class TrolleyTracker(commands.Bot):
    def __init__(self, *, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self) -> None:
        await client.load_extension("cogs.listeners")
        await client.load_extension("cogs.modcommands")
        #await client.load_extension("cogs.playcommands")
        await client.load_extension("cogs.utilitycommands")
        await self.tree.sync()
    
    async def on_ready(self):
        self.update_presence.start()
        print("ready")

    @tasks.loop(minutes=30)
    async def update_presence(self):
        guild_count = str(len(client.guilds))
        await client.change_presence(
            activity=discord.Game(name=f"Playing trolley games in {guild_count} servers! /help")
        )

intents = discord.Intents.default()
intents.members=True

client = TrolleyTracker(command_prefix = "~~~", intents=intents)

client.run(RUN_ID)