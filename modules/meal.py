import json, os, datetime
import urllib.request as ul
import urllib.parse as parse

def getSchl():
    pass

def getMeal(officeCode, schlCode, date=datetime.datetime.now().strftime("%Y%m%d")):
    url = "https://api.skybro2004.com/meal"
    url += f"?officeCode={officeCode}"
    url += f"&schlCode={schlCode}"
    url += f"&date={date}"
    
    request = ul.Request(url)
    response = ul.urlopen(url)

    if response.getcode()==200:
        responseData = response.read()
        responseData = json.loads(responseData)

        if responseData["code"]==200:
            return {"code":200, "data":responseData["meal"]}

        elif responseData["code"]==404:
            return {"code":416, "data":"급식이 없어요!"}

    else:
        return {"code":response.getcode()}



if __name__=="__main__":
    print(getMeal("J10", "7530081", "20210302"))
