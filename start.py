import discord
from discord.ext import commands
import dotenv
import os
import asyncio


dotenv.load_dotenv()

async def cogs_loader(bot):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
            except commands.ExtensionAlreadyLoaded:
                pass

async def main():
    intents = discord.Intents.default()
    intents.message_content = True  
    bot = commands.Bot(command_prefix=',', intents=intents, help_command=None)

    await cogs_loader(bot)
    print(f'whipser loaded {len(bot.cogs)} cogs')
    await bot.start(os.getenv('TOKEN'))

if __name__ == '__main__':
    dotenv.load_dotenv()
    asyncio.run(main())
