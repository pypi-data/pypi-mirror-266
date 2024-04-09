import requests

from .settings import *

def spider_auth():
    payload = {
        'grant_type': 'client_credentials',
        'client_id': 'pyspider',
        'client_secret': SPIDER_API_CLIENT_SECRET,
        'scope': 'PY_SPIDER'
    }

    res = requests.post(f'{SPIDER_API_URL}/api/oauth2/token', data=payload)
    json = res.json()

    try:
        return json['data']['accessToken']['tokenValue']
    except:
        return None
