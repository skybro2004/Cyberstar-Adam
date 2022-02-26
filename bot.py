import datetime, os, sqlite3, json

import discord

#마지막 수정시간
lastUpdateTime = datetime.datetime.fromtimestamp(os.path.getmtime(__file__)).strftime('%Y-%m-%d %H:%M:%S')

#업타임
startTime = datetime.datetime.now()

#파일 경로
path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

#모듈 불러오기
from modules import hangang

con = sqlite3.connect(f"{path}/data/database.db")
cursor = con.cursor()

keys = {}
try:
    with open(path + "/key.json", "r") as jsonKeys:
        print(path + "/key.json")
        keys = json.load(jsonKeys)
except FileNotFoundError:
    discordToken = input("디스코드 봇의 토큰을 입력하세요 : ")
    keys = {
        "discordToken" : discordToken
    }
    with open(path + "/key.json", "w") as jsonKeys:
        json.dump(keys, jsonKeys)

bot = discord.Bot()


#==================================================


@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="나잠수 - 사이버가수 아담")
    await bot.change_presence(status=discord.Status.streaming, activity=activity)
    print(f"login as {bot.user}")
    print("="*50)


#==================================================


#/ping
@bot.slash_command(guild_ids = [803249696638238750], description="Check bot's response latency")
async def ping(ctx):
    await ctx.respond(f'pong! {round(round(bot.latency, 4)*1000)}ms')

#/status
@bot.slash_command(guild_ids = [803249696638238750], description="현재 봇 상태 출력")
async def status(ctx):
    status_embed = discord.Embed(title="status", description=f"log in as {bot.user}")
    status_embed.add_field(name="ping", value=f'{round(round(bot.latency, 4)*1000)}ms')
    status_embed.add_field(name="Uptime", value=f"{str(datetime.datetime.now() - startTime).split('.')[0]}", inline=False)
    status_embed.add_field(name="last update", value=lastUpdateTime)
    status_embed.set_footer(text=f"hosting by ")
    await ctx.respond(embed=status_embed)

#/help
@bot.slash_command(name="help" , guild_ids = [803249696638238750], description="도움말을 불러옵니다.")
@bot.slash_command(name="도움말" , guild_ids = [803249696638238750], description="도움말을 불러옵니다.")
async def help(ctx):
    help_embed = discord.Embed(title='도움말')
    help_embed.add_field(name="/status", value="현재 조교봇의 상태를 불러옵니다.", inline=False)
    help_embed.add_field(name="/한강", value="한강 수온을 불러옵니다.", inline=False)
    help_embed.add_field(name="/급식", value="준비중", inline=False)
    help_embed.add_field(name="상세정보", value="[제작자 깃허브](https://github.com/skybro2004/Assistant-Bot)", inline=False)
    await ctx.respond(embed=help_embed)

#/급식
@bot.slash_command(name="급식", guild_ids = [803249696638238750], description="급식을 불러옵니다")
async def meal(ctx):
    bot.wait_for

#/시간표
@bot.slash_command(name="시간표", guild_ids = [803249696638238750], description="급식을 불러옵니다")
async def schedular(ctx):
    pass

#/한강
@bot.slash_command(name="한강", guild_ids = [803249696638238750], description="자살 하면 그만이야~")
async def getHangang(ctx):
    respondMsg = await ctx.respond(f"한강 수온을 불러오는중...")
    await respondMsg.edit_original_message(content = f"현재 한강 수온 : {hangang.getTemp()}°C")

#/dev
@bot.slash_command(name="dev", guild_ids = [803249696638238750], description="dev")
@discord.has_role(946797378780950608)
async def dev(ctx):
    await ctx.respond(f"dev")

#/owner
@bot.slash_command(name="owner", guild_ids = [803249696638238750], description="owner")
@discord.is_owner(803249696638238750)
async def hidden(ctx):
    await ctx.respond(f"owner")


bot.run(keys["discordToken"])