import discord
from discord.ext import commands
import logger
import asyncio
from db.dbfunc import is_game_channel

class Listeners(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.content.lower() == 'shutdown':
            if is_game_channel(message.channel.id):
            
                await logger.log(f'{str(message.channel)} is shutting down', self.client)

                embed = discord.Embed(title='Shutting down...', colour=discord.Color.red())
                await message.channel.send(embed=embed)
                await asyncio.sleep(2)

                await message.channel.delete()
        await self.client.process_commands(message)

async def setup(bot):
    await bot.add_cog(Listeners(bot))