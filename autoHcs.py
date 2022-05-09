import asyncio, schedule, sqlite3, os, datetime
from time import sleep
from random import randrange as random
from hcskr import selfcheck, QuickTestResult

from modules import discordModules

path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

def doHcs():
    sleep(random(1, 600))
    print()
    print("="*10, datetime.datetime.today(), "="*10)

    weekdays = ["월", "화", "수", "목", "금"]
    weekday = datetime.datetime.today().weekday()
    if 4<weekday:
        return

    con = sqlite3.connect(f"{path}/data/database.db")
    cursor = con.cursor()

    cursor.execute("select * from hcsData")
    userData = cursor.fetchall()

    userIdArr = []
    userMsgArr = []

    for data in userData:
        name = data[1]
        birth = data[2]
        region = data[3]
        school = data[4]
        level = data[5]
        password = data[6]
        if weekdays[weekday-1] in data[7]:
            quickTestResult = "negative"
        else:
            quickTestResult = "none"

        print(name, birth, region, school, level, password, quickTestResult)

        res = selfcheck(name, birth, region, school, level, password, quicktestresult=QuickTestResult[quickTestResult])
        print(res)

        userIdArr.append(data[0])
        if res["error"]==False:
            userMsgArr.append(f"{res['message']}\n자가진단 수행 시간: {res['regtime'][-8:]}")
        else:
            userMsgArr.append(f"저런! 자가진단을 수행하지 못했습니다!\n{res['message']}")

    discordModules.sendDm(userIdArr, userMsgArr)

    quit()

schedule.every().day.at("07:25").do(doHcs)

while 1:
    schedule.run_pending()
    sleep(50)
