import datetime, os, sqlite3, json, asyncio

import discord

#마지막 수정시간
lastUpdateTime = datetime.datetime.fromtimestamp(os.path.getmtime(__file__)).strftime('%Y-%m-%d %H:%M:%S')

#업타임
startTime = datetime.datetime.now()

#파일 경로
path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

#모듈 불러오기
from modules import hangang
from modules import meal

con = sqlite3.connect(f"{path}/data/database.db")
cursor = con.cursor()

keys = {}
try:
    with open(path + "/key.json", "r") as jsonKeys:
        keys = json.load(jsonKeys)
except FileNotFoundError:
    discordToken = input("디스코드 봇의 토큰을 입력하세요 : ")
    keys = {
        "discordToken" : discordToken
    }
    with open(path + "/key.json", "w") as jsonKeys:
        json.dump(keys, jsonKeys)

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)


#==================================================


@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="나잠수 - 사이버가수 아담")
    await bot.change_presence(status=discord.Status.streaming, activity=activity)
    print(f"login as {bot.user}")
    print("="*50)
    await bot.register_commands(commands=None, guild_id=803249696638238750, force=True)


#==================================================


#/ping
@bot.slash_command(guild_ids = [803249696638238750], description="Check bot's response latency")
async def ping(ctx):
    await ctx.respond(f'pong! {round(round(bot.latency, 4)*1000)}ms')

#/status
@bot.slash_command(guild_ids = [803249696638238750], description="현재 봇 상태 출력")
async def status(ctx):
    status_embed = discord.Embed(title="status", description=f"log in as {bot.user}", color=0xe74c3c)
    status_embed.add_field(name="ping", value=f'{round(round(bot.latency, 4)*1000)}ms')
    status_embed.add_field(name="Uptime", value=f"{str(datetime.datetime.now() - startTime).split('.')[0]}", inline=False)
    status_embed.add_field(name="last update", value=lastUpdateTime)
    status_embed.set_footer(text=f"hosting by ")
    await ctx.respond(embed=status_embed)

#/help
@bot.slash_command(name="help" , guild_ids = [803249696638238750], description="도움말을 불러옵니다.")
@bot.slash_command(name="도움말" , guild_ids = [803249696638238750], description="도움말을 불러옵니다.")
async def help(ctx):
    help_embed = discord.Embed(title='도움말', color=0xe74c3c)
    help_embed.add_field(name="/status", value="현재 조교봇의 상태를 불러옵니다.", inline=False)
    help_embed.add_field(name="/한강", value="한강 수온을 불러옵니다.", inline=False)
    help_embed.add_field(name="/급식", value="준비중", inline=False)
    help_embed.add_field(name="상세정보", value="[제작자 깃허브](https://github.com/skybro2004/Assistant-Bot)", inline=False)
    await ctx.respond(embed=help_embed)

#/급식
@bot.slash_command(name="급식", guild_ids = [803249696638238750], description="급식을 불러옵니다")
async def meals(ctx):
    author = ctx.author.id

    cursor.execute("SELECT id FROM userData")
    userIdList = []
    for item in cursor.fetchall():
        userIdList.append(item[0])
    
    if author in userIdList:
        cursor.execute(f"SELECT * FROM userData WHERE id={author}")
        userData = cursor.fetchone()
        todayMeal = meal.getMeal(userData[1], userData[2])
        if todayMeal["code"]==200:
            mealEmbed = discord.Embed(title=f"{datetime.datetime.now().strftime('%m월 %d일')} 급식", color=0xe74c3c)
            for item in todayMeal["data"]:
                mealEmbed.add_field(name=item["name"], value=", ".join(item["allergy"]), inline=False)
            mealEmbed.set_footer(text=f"{todayMeal['cal']}")

            await ctx.respond(embed=mealEmbed)
        elif todayMeal["code"]==416:
            await ctx.respond("오늘은 급식이 없습니다.")
        else:
            await ctx.respond(f"알 수 없는 에러가 발생했습니다.\nError no.{todayMeal['code']}")

        await ctx.respond(embed=mealEmbed)

    else:
        botMsg = await ctx.respond("학교 이름을 입력해주세요")

        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == botMsg.channel.id

        while 1:
            try:
                userMsg = await bot.wait_for("message", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await botMsg.edit_original_message(content="타임아웃")
                return
            else:
                schlName = userMsg.content
                await userMsg.delete()

                schlData = meal.getSchl(schlName)

                if schlData["code"]==200:
                    break

                elif schlData["code"]==416:
                    await botMsg.edit_original_message(content="학교가 검색되지 않았어요.\n다시 입력해주세요")

                else:
                    await botMsg.edit_original_message(content=f"알 수 없는 에러가 발생했어요.\nError no.{schlData['code']}")
                    return

        schlData = schlData["schools"]
        schools = []
        for school in schlData:
            schools.append(discord.SelectOption(label=school["schlName"], description=school["office"], value=json.dumps({"schlCode":school["schlCode"], "officeCode":school["officeCode"]})))

        global selection
        selection = ""

        class selectSchl(discord.ui.View):
            @discord.ui.select(placeholder="학교를 선택하세요", options=schools)
            async def select(self, select: discord.ui.Select, interaction: discord.Interaction):
                if author==interaction.user.id:
                    global selection
                    selection = json.loads(interaction.data["values"][0])


            @discord.ui.button(label="확인")
            async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
                if author==interaction.user.id:
                    global selection
                    if selection=="":
                        await ctx.respond("학교를 선택해주세요!", ephemeral=True)
                    else:
                        try:
                            #DB에 저장
                            cursor.execute(
                                "INSERT INTO userData(id, officeCode, schlCode) VALUES(?, ?, ?)",
                                (author, selection["officeCode"], selection["schlCode"])
                            )

                        except sqlite3.IntegrityError: #이미 등록한 사용자의 경우
                            #정보업데이트
                            cursor.execute(
                                "UPDATE userData SET officeCode=?, schlCode=? WHERE id=?",
                                (selection["officeCode"], selection["schlCode"], author)
                            )

                        con.commit()

                        await botMsg.edit_original_message(content="설정 완료!", view=None, delete_after=5.0)

        await botMsg.edit_original_message(content=f"\"{schlName}\" 검색결과", view=selectSchl())




#/시간표
@bot.slash_command(name="시간표", guild_ids = [803249696638238750], description="시간표 불러옵니다")
async def schedular(ctx):
    pass

#/한강
@bot.slash_command(name="한강", guild_ids = [803249696638238750], description="자살 하면 그만이야~")
async def getHangang(ctx):
    respondMsg = await ctx.respond(f"한강 수온을 불러오는중...")
    await respondMsg.edit_original_message(content = f"현재 한강 수온 : {hangang.getTemp()}°C")

#/dev
@bot.slash_command(name="dev1", guild_ids = [803249696638238750], description="dev1")
@discord.has_role(946797378780950608)
async def dev1(ctx):
    class dropdown(discord.ui.View):
        @discord.ui.select(placeholder="asdf", options=[discord.SelectOption(label="test", value="value"), discord.SelectOption(label="test2", value="value2", description="des")])
        async def textfield(self, select: discord.ui.Select, interaction: discord.Interaction):
            print(interaction.data)

        @discord.ui.button(label="asdf", style=discord.ButtonStyle.primary)
        async def primary(self, button: discord.ui.Button, interaction: discord.Integration):
            await ctx.respond("buttonpress")

    await ctx.respond("dropdown", view=dropdown())

@bot.slash_command(name="dev2", guild_ids = [803249696638238750], description="dev2")
@discord.has_role(946797378780950608)
async def dev2(ctx):
    

    await ctx.respond("dropdown")

#/owner
@bot.slash_command(name="owner", guild_ids = [803249696638238750], description="owner")
@discord.is_owner(803249696638238750)
async def hidden(ctx):
    print(bot.guilds)
    await ctx.respond(f"owner")

@bot.slash_command(name="test", guild_ids = [803249696638238750], description="test")
async def hidden(ctx):
    await ctx.respond(f"owner")


bot.run(keys["discordToken"])