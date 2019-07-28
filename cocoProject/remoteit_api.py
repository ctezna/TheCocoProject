import requests
import json
import os

def login(key,username,password):
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
    
    try:
        return(response_body['token'])
        pass
    except KeyError as ke:
        return(800)
        pass

def connect(key, token, address):
    headers = {
        "developerkey": key,
        # Created using the login API
        "token": token
    } 
    body = {
        "deviceaddress": address
    }
    url = "https://api.remot3.it/apv/v27/device/connect"
    response = requests.post(url, data=json.dumps(body), headers=headers)
    response_body = response.json()
    try:
        return(response_body['connection']['expirationsec'] + ";" + response_body['connection']['proxy'])
        pass
    except KeyError as ke:
        return(801)
        pass