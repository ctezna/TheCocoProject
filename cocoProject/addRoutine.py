import requests
import json, datetime

def send(proxy, task, days, times):
    url = proxy + '/routine'
    headers = {
        "date": 'datetime.date()'
    }
    body = {
        "task": task,
        "days": days,
        "times": times
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    #response_body = response.json()
    #print(response_body)
    return 0