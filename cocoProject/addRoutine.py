import requests
import json, datetime

def send(proxy, task, days, times):
    url = proxy + '/routine'
    headers = {
        "Content-Type": 'application/json'
    }
    body = {
        "task": task,
        "days": days,
        "times": times
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    #response_body = response.json()
    print(response)
    return 0