# coding:utf-8
import requests

def get_jsapi_ticket(appid, secrect):
    token = get_Token(appid, secrect)
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=' + token + '&type=jsapi'
    r = requests.get(url)
    print r.json()
    jsapi_ticket = r.json()['ticket']
    return jsapi_ticket


def get_Token(appid, secrect):
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
        appid, secrect)
    result = requests.get(url)
    r = result.json()
    token = r['access_token']
    print 'token::::' + token
    return token