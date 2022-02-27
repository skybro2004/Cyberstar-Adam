import json, os, datetime
import urllib.request as ul
import urllib.parse as parse

key = "028278aaacd242438668d46a5464e934"

def getSchl(schlName):
    #url 정하기
    url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={key}&Type=json&pSize=25"
    url += f"&SCHUL_NM={parse.quote(schlName)}"
    #요청
    request = ul.Request(url)
    #응답
    response = ul.urlopen(request)

    #정상적으로 불러옴
    if response.getcode()==200:
        #응답 데이터 읽기
        responseData = response.read()
        #json으로 디코드
        responseData = json.loads(responseData)

        try:
            schlCount = responseData["schoolInfo"][0]["head"][0]["list_total_count"]
            #데이터 정제
            responseData = responseData["schoolInfo"][1]["row"]
            schools = []
            #필요한 데이터(학교 이름, 도,시 이름, 학교 코드, 도,시 코드)만 뽑아와서 school 배열 안에 정리
            for i in range(schlCount):
                schools.append({"schlName":responseData[i]["SCHUL_NM"], "schlCode":responseData[i]["SD_SCHUL_CODE"], "office":responseData[i]["LCTN_SC_NM"], "officeCode":responseData[i]["ATPT_OFCDC_SC_CODE"]})
            #리턴
            return {"code":200, "schlCount":schlCount, "schools":schools}

        except: #학교가 검색되지 않았을때
            return {"code":416}
        
    #api 에러
    else:
        return {"code":response.getcode()}



def getMeal(officeCode, schlCode, date=datetime.datetime.now().strftime("%Y%m%d")):
    url = "https://api.skybro2004.com/meal"
    url += f"?officeCode={officeCode}"
    url += f"&schlCode={schlCode}"
    url += f"&date={date}"
    
    request = ul.Request(url)
    response = ul.urlopen(request)

    if response.getcode()==200:
        responseData = response.read()
        responseData = json.loads(responseData)

        if responseData["code"]==200:
            return {"code":200, "data":responseData["meal"], "cal":responseData["cal"]}

        elif responseData["code"]==404:
            return {"code":416, "data":"급식이 없어요!"}

    else:
        return {"code":response.getcode()}



if __name__=="__main__":
    print(getSchl("서현"))
    print(getMeal("J10", "7530081", "20210302"))
