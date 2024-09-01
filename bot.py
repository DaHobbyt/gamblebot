import discord
from discord.ext import commands
import aiosqlite
import aiohttp
import requests
from config import *


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('gg/notnomv6 for bots!'))

bot.load_extension('cogs.credit_system')
bot.load_extension('cogs.dice_game')
bot.load_extension('cogs.roulette_game')
bot.load_extension('cogs.coinflip')
bot.load_extension('cogs.withdraw')
bot.load_extension('cogs.help')
bot.load_extension('cogs.suggestions')
bot.load_extension('cogs.crash')
bot.load_extension('cogs.rps')

bot.run(token)