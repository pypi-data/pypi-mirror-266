import requests


# JSON Format
# {
#  "time": 32,
#  "energy": 0.5
# }
#

def send(url, time, energy):
    reply = requests.post(url=url, json={"time": time, "energy": energy})
    if reply.status_code == 200:
        return True
    else:
        return False