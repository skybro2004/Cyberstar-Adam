import urllib.request as ul
import json

#한강수온 리턴
def getTemp():
    #url 정하기
    url = "https://api.hangang.msub.kr/"
    #요청
    request = ul.Request(url)
    #응답
    response = ul.urlopen(request)
    #응답 데이터 읽기
    responseData = response.read()
    #json 디코드
    responseData = json.loads(responseData)
    #수온 리턴
    return responseData["temp"]

#디버그용
if __name__=="__main__":
    print(getTemp())
