import json, os


path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
path = "/".join(path.split("/")[:-1]) + "/data/images/"


with open(path + "hash.json") as hashJson:
    hashMap = json.load(hashJson)


def makeUrl(imageName):
    try:
        return path + hashMap[imageName]
    except KeyError:
        return path + "404/몰루.gif"