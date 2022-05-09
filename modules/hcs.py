import json
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
            #필요한 데이터만 뽑아와서 school 배열 안에 정리
            #학교이름, 학교종류, 지역이름
            for i in range(schlCount):
                schools.append({"schlName":responseData[i]["SCHUL_NM"], "schlLvl":responseData[i]["SCHUL_KND_SC_NM"], "office":responseData[i]["LCTN_SC_NM"]})
            #리턴
            return {"code":200, "schlCount":schlCount, "schools":schools}

        except: #학교가 검색되지 않았을때
            return {"code":416}
        
    #api 에러
    else:
        return {"code":response.getcode()}