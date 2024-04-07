__all__ = ['discord_check']

import time
import requests

def logActive(token):
    with open('tokenActive.txt', 'a') as f:
        f.write(token + '\n')

def logBan(token):
    with open('tokenBan.txt', 'a') as f:
        f.write(token + '\n')

def check(authToken):
    url = "https://discord.com/api/v9/users/@me/billing/country-code"

    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': authToken,
        'X-Discord-Locale': 'en-GB',
        'X-Debug-Options': 'bugReporterEnabled',
        'Origin': 'https://discord.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Content-Length': '0',
        'TE': 'trailers'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload, timeout=30)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(e)
        time.sleep(1)
        check(authToken)

def token(authToken):
    if check(authToken):
        print('\tToken is active! ', authToken[:40])
        logActive(authToken)

    else:
        print('\tToken is not active! ', authToken[:40])
        logBan(authToken)

def file(file):
    with open(file, 'r') as f:
        tokens = f.read().split('\n')
    for authToken in tokens:
        if authToken:
            token(authToken)
