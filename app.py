import sys
import asyncio
import discord
from discord.ext import commands
# Windows 專用事件循環補丁,防止 Windows 系統頻繁關閉時底層 Socket 發生死鎖
if sys.platform == 'win32':
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
