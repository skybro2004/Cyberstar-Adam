import asyncio, schedule, sqlite3, os, datetime, time
from hcskr import selfcheck, QuickTestResult

path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

def doHcs():
    weekdays = ["월", "화", "수", "목", "금"]
    weekday = datetime.datetime.today().weekday()
    if 4<weekday:
        return

    con = sqlite3.connect(f"{path}/data/database.db")
    cursor = con.cursor()

    cursor.execute("select * from hcsData")
    userData = cursor.fetchall()

    for data in userData:
        print(data, type(data))
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

        print(name, birth, region, school, level, birth, quickTestResult)

        data = selfcheck(name, birth, region, school, level, password, quicktestresult=QuickTestResult[quickTestResult])
        print(data)

    quit()



schedule.every().day.at("07:30").do(doHcs)

while 1:
    schedule.run_pending()
    time.sleep(50)