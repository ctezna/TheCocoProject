import requests
import json, datetime

def send(routineId, proxy, task, days, times):
    url = proxy + '/addRoutine'
    payload = {
        "routine_id": routineId,
        "task": task,
        "days": days,
        "times": times
    }
    try:
        response = requests.get(url, params=payload)
        response_body = response.json()
        print(response_body)
        return 1
    except:
        return 0


def remove(routineId, proxy):
    url = proxy + '/removeRoutine'
    payload = {
        "routine_id": routineId
    }
    try:
        response = requests.get(url, params=payload)
        response_body = response.json()
        print(response_body)
        return 1
    except:
        return 0

def get(proxy):
    url = proxy + '/getRoutines'
    try:
        response = requests.get(url)
        response_body = response.json()
        print(response_body)
        return response_body
    except:
        return 0