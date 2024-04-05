import json
from time import gmtime, strftime

__cube = {
    1: "",
    2: "",
    3: "",
    4: "",
    5: "",
    6: "",
    7: "",
    8: ""
}

def setPos(int, value):
    __cube[int] = value

def getPos(int):
    return __cube[int]


def getjson():
    data = {'time': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            'config': {'1': getPos(1), '2': getPos(2), '3': getPos(3), '4': getPos(4), '5': getPos(5), '6': getPos(6),
                       '7': getPos(7), '8': getPos(8)}}
    return json.dumps(data)

def getconfig():
    data = {'config': {'1': getPos(1), '2': getPos(2), '3': getPos(3), '4': getPos(4), '5': getPos(5), '6': getPos(6),
                       '7': getPos(7), '8': getPos(8)}}
    return json.dumps(data)
