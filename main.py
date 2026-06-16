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
# 核心全域資料庫狀態機
game = {
"is_active": False, # 遊戲是否進行中的狀態開關
"players": [], # 存放已報名玩家 Member 物件的 List容器
"words": {}, # 儲存每個人分到的詞彙 {玩家ID: "詞彙"}
"identities": {}, # 儲存每個人的身分 {玩家ID: "角色"}
"undercover_id": None, # 紀錄誰是臥底的用戶ID
"voted_users": {} # 紀錄投票矩陣 {投票者ID: 被投票者ID}
}
@bot.event
async def on_ready():
print(f'🤖 遊戲主機已成功對接連線:{bot.user.name}')
@bot.command(name="報名")
async def sign_up(ctx):
if game["is_active"]:
await ctx.send("⚠️ 遊戲已經在進行中,請等下一局!")
return
# 檢查該用戶物件是否已存在於 List 容器內,防止重複報名
if ctx.author in game["players"]:
await ctx.send(f"❓ {ctx.author.mention} 你已經報名過了,請勿重複註冊!")
return
# 動態將發出指令的玩家物件塞進列表尾端
game["players"].append(ctx.author)
await ctx.send(f"✅ {ctx.author.mention} 報名成功!目前房間總人數:{len(game['players'])} 人")
