import discord

def sendDm(userIdArr, messages):
    #봇에게 권한 부여
    intents = discord.Intents.all()
    #시작
    bot = discord.Bot(intents=intents)

    @bot.event
    async def on_ready():
        for i in range(len(userIdArr)):
            try:
                user = await bot.fetch_user(userIdArr[i])
                await user.send(messages[i])
            except:
                pass
        await bot.close()


    bot.run("OTQ2NzY2MDQ3NTYwNzYxMzY1.Yhjelw.Ns4PpuhwffpcpEHZ43zyNZimxy4")


if __name__=="__main__":
    sendDm([687207594594402332], ["테스트테트리스트테스트"])