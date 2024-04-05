import requests, json


def checkCloudStatus(url):
    try:
        reply = requests.post(url)
        if reply.status_code == 200:
            return True
        if reply.status_code == 401:
            return True
        else:
            return False
    except requests.exceptions.HTTPError as err:
        return False



def __getData(url, devid, authkey):
    if (checkCloudStatus(url)):
        data = {'id': devid, 'auth_key': authkey}
        reply = requests.post(url, data=data)
        return reply.content
    else:
        return "Not connected"


def getEnergyTotal(url, devid, authkey):
    if (checkCloudStatus(url)):
        j = json.loads(__getData(url, devid, authkey))
        return j["data"]["device_status"]["switch:0"]["aenergy"]["total"]
    else:
        return "Not connected"
