import requests
import json
import os

def connect(key,username,password,address):
    # need to change to env variables
    headers = {
        "developerkey": key
    }
    body = {
        "password": password,
        "username": username
    }
    url = "https://api.remot3.it/apv/v27/user/login"

    response = requests.post(url, data=json.dumps(body), headers=headers)
    response_body = response.json()

    # print("Status Code: %s" % response.status_code)
    # print("Raw Response: %s" % response.raw)
    # print("Body: %s" % response_body)

    headers = {
        "developerkey": key,
        # Created using the login API
        "token": response_body['token']
    } 
    body = {
        "deviceaddress": address
    }
    url = "https://api.remot3.it/apv/v27/device/connect"
    response = requests.post(url, data=json.dumps(body), headers=headers)
    response_body = response.json()
    return(response_body['connection']['proxy'])