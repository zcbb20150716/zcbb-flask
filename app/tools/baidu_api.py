# coding:utf-8
import requests
import datetime
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

weather_key = "zuingudcowmtmj8t"
baidu_key = "ngCytQb9U88h58PGDgW6Yiuv"
baidu_secret = "c67f2f29a9e783ed14acbeff5588772c"
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit'
                      '/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safar'
                      'i/537.36',
    }

def get_baidu_api_token():
    token_data = {
        "grant_type":"client_credentials",
        "client_id":baidu_key,
        "client_secret":baidu_secret
    }
    get_token = requests.post("https://openapi.baidu.com/oauth/2.0/token",data=token_data)
    return get_token.json()


def get_weather():
    base_url = "https://api.seniverse.com/v3"
    url = base_url+"/weather/now.json"
    data = {
        "key": weather_key,
        "location": "tianjin",
        "language": "zh-Hans",
        "unit": "c"
    }


    r = requests.get(url=url, params=data, headers=headers)
    return r.json()["results"][0]["now"]


def create_weather_file(p):
    _dict = get_weather()
    weather = _dict["text"]
    temp = _dict["temperature"]
    # humidity = _dict["humidity"]
    # wind_direction = _dict["wind_direction"]
    # wind_speed = _dict["wind_speed"]
    # wind_scale = _dict["wind_scale"]
    day = datetime.datetime.now().strftime('%H')
    if int(day) >0 and int(day)<4:
        time = "凌晨"
        text = "期待有一个新的开始"
    elif int(day)>=4 and int(day)<12:
        time = "上午"
        text = "祝你工作生活愉快"
    elif int(day)>=12 and int(day) <20:
        time = "下午"
        text = "祝你工作生活愉快"
    else:
        time = "晚上"
        text = "注意休息"
    _text = '%s好 刘箴初小朋友！现在是%s,天气%s,温度%s摄氏度,%s' % \
           (time, datetime.datetime.now().strftime('%Y年%m月%d日 %H时%M分%S秒'),
            weather, temp, text)
    url = 'http://tsn.baidu.com/text2audio'
    data = {
        "tex": _text,
        "lan": "zh",
        "tok": get_baidu_api_token()["access_token"],
        "ctp": "1",
        "cuid": "zcbb",
        "spd": "4",
        "pit": "4",
        "vol": "4",
        "per": "0"
    }
    res = requests.get(url, params=data, headers=headers)
    print res.status_code
    path = '/var/www/html/we-%s.mp3' % p
    with open(path, 'wb') as f:
        f.write(res.content)
    os.system('mplayer %s' % path)
    return path, _text


def create_ai_file(_text, p):

    url = 'http://tsn.baidu.com/text2audio'
    data = {
        "tex": _text,
        "lan": "zh",
        "tok": get_baidu_api_token()["access_token"],
        "ctp": "1",
        "cuid": "zcbb",
        "spd": "4",
        "pit": "4",
        "vol": "4",
        "per": "0"
    }
    res = requests.get(url, params=data, headers=headers)
    path = '/var/www/html/ai-%s.mp3' % p
    with open(path, 'wb') as f:
        f.write(res.content)
    os.system('mplayer %s' % path)

    return path, _text


if __name__ == "__main__":
    create_weather_file()
    print u"执行成功，请收听天气预报..o O O O o .."
