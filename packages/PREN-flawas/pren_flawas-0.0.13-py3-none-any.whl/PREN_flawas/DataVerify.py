import requests, json
from requests.structures import CaseInsensitiveDict

def checkAvailability(url):
    payload = {}
    headers = {}

    response = requests.request("GET", url)
    if response.status_code == 200:
        return True
    else :
        return False


def sendStatus(url, token):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Auth"] = token
    resp  = requests.post(url, headers=headers)
    if resp.status_code == 204:
        return True
    else:
        return False


def sendData(url, token, time, config):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Auth"] = token
    data = {"time": time,
            "config": config}
    print(data)
    resp = requests.post(url, headers=headers, data=config)
    if resp.status_code == 200:
        return True
    else:
        return False