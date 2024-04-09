import json
import re

import requests

from AndroidQQ.http import User_Agent
from AndroidQQ.utils import qq_bkn


def change_psw_getsms(info, Cookie: str, mobile: str):
    match = re.search(r'skey=([^;]+)', Cookie)
    if match:
        skey = match.group(1)
    else:
        skey = None

    try:

        Cookie = Cookie + 'domainid=761'
        response = requests.post(
            url="https://accounts.qq.com/v2/cn2/change_psw/proxy/domain/qq110.qq.com/v3/getsms",
            params={
                "bkn": qq_bkn(skey),
            },
            headers={
                "Host": "accounts.qq.com",
                "Connection": "keep-alive",
                "Content-Length": "109",
                "Accept": "application/json, text/plain, */*",
                "qname-service": "1935233:65536",
                "qname-space": "Production",
                "User-Agent": User_Agent,
                "Content-Type": "application/json",
                "Origin": 'https://accounts.qq.com',
                "X-Requested-With": "com.tencent.mobileqq",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://accounts.qq.com/cn2/change_psw/mobile/mobile_change_psw_way?source_id=3259&uin=" + info.uin,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": Cookie,

            },
            data=json.dumps({
                "com": {
                    "version": "8.9.83",
                    "scene": 304,
                    "src": 1,
                    "platform": 2
                },
                "areaCode": "+86",
                "way": 3,
                "mobile": mobile
            }),
            proxies=info.proxy_proxies

        )

        return response.json()
    except requests.exceptions.RequestException:
        print('发送短信失败')
        return {}
