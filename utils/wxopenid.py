import requests
from django.conf import settings

OPENID_URL = settings.OPENID_URL
APPID = settings.APPID
AppSecret = settings.APPSECRET


def get_openid(jscode, OPENID_URL=OPENID_URL, APPID=APPID, AppSecret=AppSecret):
    url = OPENID_URL + "?appid=" + APPID + "&secret=" + AppSecret + "&js_code=" + jscode + "&grant_type=authorization_code"
    r = requests.get(url)
    response_msg = r.json()
    # openid = r.json()['openid']
    return response_msg
