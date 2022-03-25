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

#데이터베이스 불러오기
con = sqlite3.connect(f"{path}/data/database.db")
cursor = con.cursor()

#투표 데이터
voteDatas = {}

#디스코드 봇 토큰 불러오기
keys = {}
try:
    with open(path + "/key.json", "r") as jsonKeys:
        keys = json.load(jsonKeys)
#토큰이 없다면 입력받아 저장하기
except FileNotFoundError:
    discordToken = input("디스코드 봇의 토큰을 입력하세요 : ")
    keys = {
        "discordToken" : discordToken
    }
    with open(path + "/key.json", "w") as jsonKeys:
        json.dump(keys, jsonKeys)

#봇에게 권한 부여
intents = discord.Intents.all()
#시작
bot = discord.Bot(intents=intents)


#==================================================


#로그인시 할 행동
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
async def meals(
        ctx,
        date: discord.Option(str, name="날짜", description="급식을 불러올 날짜를 선택합니다. YYMMDD 형식으로 입력받습니다.", default=datetime.date.today().strftime("%Y%m%d")),
        mode: discord.Option(str, description="등록: 저장된 사용자 정보를 등록/수정합니다.", choices=["등록"], required=False)
    ):

    #날짜 포매팅
    if date=="오늘":
        date = datetime.date.today().strftime("%Y%m%d")
    elif date=="내일":
        date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y%m%d")
    elif len(date)==4:
        date = str(datetime.date.today().year) + date
    elif len(date)==6:
        date = "20" + date
    elif len(date)==8:
        pass
    else:
        await ctx.respond("날짜 입력 형식이 잘못되었어요!")
        return

    #사용자 아이디 임시 저장
    author = ctx.author.id

    #저장된 사용자 데이터 중 아이디 불러오기
    cursor.execute("SELECT id FROM userData")
    userIdList = []
    for item in cursor.fetchall():
        userIdList.append(item[0])

    #급식 불러오기
    if (author in userIdList) and mode!="등록":
        #사용자 데이터 불러오기
        cursor.execute(f"SELECT * FROM userData WHERE id={author}")
        userData = cursor.fetchone()
        #meal 모듈을 통해 급식 정보 불러오기
        todayMeal = meal.getMeal(userData[1], userData[2], date)

        #정상
        if todayMeal["code"]==200:
            mealStr = []
            for item in todayMeal["data"]:
                mealStr.append(item["name"])
            mealStr = "\n".join(mealStr)
            mealEmbed = discord.Embed(title=f"{int(date[4:6])}월 {int(date[6:8])}일 급식", description=mealStr, color=0xe74c3c)
            mealEmbed.set_footer(text=f"{todayMeal['cal']}")

            await ctx.respond(embed=mealEmbed)

        #급식이 없음
        elif todayMeal["code"]==416:
            await ctx.respond("급식이 없습니다.")

        #알 수 없는 에러
        else:
            await ctx.respond(f"알 수 없는 에러가 발생했습니다.\nError no.{todayMeal['code']}")

    #사용자 정보 등록
    else:
        botMsg = await ctx.respond("학교 이름을 입력해주세요")

        #wait_for 대응 함수(메시지 작성자가 등록중인 사용자인가?)
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == botMsg.channel.id

        #학교 이름 입력받기
        while 1:
            #메시지 입력 대기
            try:
                userMsg = await bot.wait_for("message", timeout=30.0, check=check)
            #타임아웃
            except asyncio.TimeoutError:
                await botMsg.edit_original_message(content="타임아웃")
                return
            #메시지 입력 후
            else:
                schlName = userMsg.content
                await userMsg.delete()

                schlData = meal.getSchl(schlName)

                #학교 검색 성공
                if schlData["code"]==200:
                    break

                #학교 검색 결과 없으면 다시 입력
                elif schlData["code"]==416:
                    await botMsg.edit_original_message(content="학교가 검색되지 않았어요.\n다시 입력해주세요")
                    continue

                #에러
                else:
                    await botMsg.edit_original_message(content=f"알 수 없는 에러가 발생했어요.\nError no.{schlData['code']}")
                    return

        #학교 목록 불러오기
        schlData = schlData["schools"]
        schools = []
        for school in schlData:
            schools.append(discord.SelectOption(label=school["schlName"], description=school["office"], value=json.dumps({"schlCode":school["schlCode"], "officeCode":school["officeCode"]})))

        #사용자 선택 저장용 글로벌 변수
        global selection
        selection = ""

        #컴포넌트 클래스
        class selectSchl(discord.ui.View):
            #학교 목록 컴포넌트
            @discord.ui.select(placeholder="학교를 선택하세요", options=schools)
            async def select(self, select: discord.ui.Select, interaction: discord.Interaction):
                #선택
                #인터랙션한 사용자==등록중인 사용자인가
                if author==interaction.user.id:
                    #아까 만든 변수에 선택한 값 저장
                    global selection
                    selection = json.loads(interaction.data["values"][0])

            #확인 버튼 컴포넌트
            @discord.ui.button(label="확인", style=discord.ButtonStyle.green)
            async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
                #선택 완료
                #인터랙션한 사용자==등록중인 사용자인가
                if author==interaction.user.id:
                    #아까 만든 변수 불러오기
                    global selection
                    #아무것도 선택 안했을때
                    if selection=="":
                        await ctx.respond("학교를 선택해주세요!", ephemeral=True)

                    else:
                        try:
                            #선택한 학교 DB에 저장
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

                        #DB 적용
                        con.commit()

                        #설정 완료 얼럿(5초후 자동 삭제)
                        await botMsg.edit_original_message(content="설정 완료!", view=None, delete_after=5.0)

        #학교 검색결과 컴포넌트와 함께 표시
        await botMsg.edit_original_message(content=f"\"{schlName}\" 검색결과", view=selectSchl())


#/시간표
@bot.slash_command(name="시간표", guild_ids = [803249696638238750], description="시간표 불러옵니다")
async def schedular(ctx):
    pass


#/투표
class Vote:
    def __init__(self):
        self.voteData = {}
    def addVote(self, userId, data):
        if userId in self.voteData.keys():
            raise Exception("alreadyVotedError")
        self.voteData[userId] = data
    def getVote(self):
        return self.voteData

class VoteButton:
    def __init__(self):
        pass
    @discord.ui.button()
    def asdf(self, button: discord.ui.Button):
        discord.ui.Button()


@bot.slash_command(name="투표", guild_ids = [803249696638238750], description="준비중")
async def vide(
        ctx,
        mode: discord.Option(bool, name="찬반투표", description="asdf", default=True),
        subject: discord.Option(str, name="주제", description="투표의 주제를 입력하세요.", required=False),
        cases: discord.Option(str, name="안건", description="안건을 입력받습니다. \",\"로 구분합니다.", default=None)
    ):

    view = discord.ui.View()

    voteEmbed = discord.Embed(title="!투표", description=f"주제: {subject}")

    if mode==True:
        buttonAgree = discord.ui.Button(emoji="✔", style=discord.ButtonStyle.green)
        buttonDisagree = discord.ui.Button(emoji="✖", style=discord.ButtonStyle.red)
        voteEmbed.add_field(name="찬성", value="0", inline=True)
        voteEmbed.add_field(name="반대", value="0", inline=True)
        async def agreeCallback(interaction):
            print(interaction.message.content)
            print(interaction.custom_id)
            print(interaction.id)
            voteDatas[interaction.message.id].addVote(interaction.user.id, True)
        async def disagreeCallback(interaction):
            voteDatas[interaction.message.id].addVote(interaction.user.id, False)
        buttonAgree.callback = agreeCallback
        buttonDisagree.callback = disagreeCallback
        view.add_item(buttonAgree)
        view.add_item(buttonDisagree)

    else:
        if (not "," in cases) or (cases.startswith(",")) or (cases.endswith(",")):
            ctx.respond("안건을 최소 1개 이상 입력해주세요!")
            return
        cases = cases.split(",")

    voteMsg = await ctx.respond(embed=voteEmbed, view=view)

    print(voteMsg.id)

    buttonAgree.custom_id = voteMsg.id

    voteDatas[voteMsg.id] = Vote()
    print(voteDatas)




    #voteDatas[id].addVote(userId, data)

    pass


#/한강
@bot.slash_command(name="한강", guild_ids = [803249696638238750], description="자살 하면 그만이야~")
async def getHangang(ctx):
    """한강 api 딜레이 심해서 디코봇이 응답안함으로 인식함. 그래서 일단 메시지 보내고 수정하는 방식 채용"""

    respondMsg = await ctx.respond(f"한강 수온을 불러오는중...")
    await respondMsg.edit_original_message(content = f"현재 한강 수온 : {hangang.getTemp()}°C")


#/dev
@bot.slash_command(name="dev1", guild_ids = [803249696638238750], description="dev1")
@discord.has_role(946797378780950608)
async def dev1(ctx):
    aasdff = discord.ui.Button(label="asdf")


@bot.slash_command(name="dev2", guild_ids = [803249696638238750], description="dev2")
@discord.has_role(946797378780950608)
async def dev2(ctx):
    voteList = discord.ui.Select(placeholder="기호6번허경영", options=[discord.SelectOption(label="기호1번찢재명", value=1), discord.SelectOption(label="기호2번퐁퐁이형", value=2)])
    view = discord.ui.View()
    view.add_item(voteList)
    await ctx.respond("투표", view=view)

@bot.slash_command(name="dev3", guild_ids = [803249696638238750], description="dev3")
@discord.has_role(946797378780950608)
async def dev3(ctx):
    #voteList = discord.ui.Select(placeholder="기호6번허경영", options=[discord.SelectOption(label="기호1번찢재명", value=1), discord.SelectOption(label="기호2번퐁퐁이형", value=2)])
    inputText = discord.ui.InputText(label="label", placeholder="placeholder", value="asdf")
    view = discord.ui.View()
    view.add_item(inputText)
    await ctx.respond("투표", view=view)


#/owner
@bot.slash_command(name="owner", guild_ids = [803249696638238750], description="owner")
@discord.is_owner(803249696638238750)
async def hidden(ctx):
    print(bot.guilds)
    await ctx.respond(f"owner")


#/buttonTest
@bot.slash_command(name="button_test", guild_ids = [803249696638238750], description="test")
async def hidden(ctx):
    button = discord.ui.Button(label="<:white_check_mark:> asfd", style=discord.ButtonStyle.green, emoji="✔")
    components = discord.ui.View()
    components.add_item(button)
    await ctx.respond("awsdf", view=components)



#봇 실행
bot.run(keys["discordToken"])