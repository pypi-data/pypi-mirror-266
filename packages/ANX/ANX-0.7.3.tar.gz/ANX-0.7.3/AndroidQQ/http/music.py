import gzip
import hashlib
import json
import re
import time
from io import BytesIO
from urllib.parse import urlparse, parse_qs

import requests

from AndroidQQ.http import User_Agent
from AndroidQQ.utils import qq_bkn


def music_sign(data):
    k1 = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
    }
    l1 = [212, 45, 80, 68, 195, 163, 163, 203, 157, 220, 254, 91, 204, 79, 104, 6]
    t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    md5_bytes = hashlib.md5(data.encode()).hexdigest().upper()
    t1 = md5_bytes[21] + md5_bytes[4] + md5_bytes[9] + md5_bytes[26] + md5_bytes[16] + md5_bytes[20] + md5_bytes[27] + \
         md5_bytes[30]
    t3 = md5_bytes[18] + md5_bytes[11] + md5_bytes[3] + md5_bytes[2] + md5_bytes[1] + md5_bytes[7] + md5_bytes[6] + \
         md5_bytes[25]
    ls2 = []
    for i in range(16):
        x1 = k1[md5_bytes[i * 2]]
        x2 = k1[md5_bytes[i * 2 + 1]]
        x3 = ((x1 * 16) ^ x2) ^ l1[i]
        ls2.append(x3)
    ls3 = []
    for i in range(6):
        if i == 5:
            ls3.append(t[ls2[len(ls2) - 1] >> 2])
            ls3.append(t[(ls2[len(ls2) - 1] & 3) << 4])
        else:
            x4 = ls2[i * 3] >> 2
            x5 = (ls2[i * 3 + 1] >> 4) ^ ((ls2[i * 3] & 3) << 4)
            x6 = (ls2[i * 3 + 2] >> 6) ^ ((ls2[i * 3 + 1] & 15) << 2)
            x7 = 63 & ls2[i * 3 + 2]
            ls3.extend([t[x4], t[x5], t[x6], t[x7]])
    t2 = ''.join(ls3).replace("/", "")
    sign = "zzb" + (t1 + t2 + t3).lower()
    return sign


class Music:
    def __init__(self, info):
        self.qm_keyst = None
        self.cookies = None
        self.uin = info.uin
        self.client_key = info.cookies.client_key
        self.code = None
        self.g_tk = None
        self.psrf_qqopenid = None
        self.info = info

    def get_Location_code(self):
        if not self.client_key:
            return {'status': False, 'message': '没有获取到clientkey'}
        try:
            response = requests.get(url="https://ssl.ptlogin2.qq.com/jump",
                                    params={
                                        "keyindex": "19",
                                        "clientuin": self.uin,
                                        "clientkey": self.client_key,
                                        "u1": "https://connect.qq.com",
                                        "pt_report": "1",
                                        "pt_aid": "716027609",
                                        "daid": "383",
                                        "style": "35",
                                        "pt_ua": "76BA0A6746DFE83A98D8D2F11E2D88FF",
                                        "pt_browser": "others",
                                        "pt_3rd_aid": "100497308",
                                        'pt_openlogin_data': f'appid=716027609&pt_3rd_aid=100497308&daid=383&pt_skey_valid=1&style=35&s_url=https%3A%2F%2Fconnect.qq.com&refer_cgi=authorize&which=&sdkp=pcweb&sdkv=v1.0&time={str(int(time.time()))}&loginty=3&h5sig=eGKHXAcp1AAAlR38DBo6E_oj3OrsS53GtW1_bmkcOzY&response_type=code&client_id=100497308&redirect_uri=https%3A%2F%2Fy.qq.com%2Fm%2Flogin%2Fredirect.html%3Fis_qq_connect%3D1%26login_type%3D1%26surl%3Dhttps%253A%252F%252Fi.y.qq.com%252Fn2%252Fm%252Fclient%252Factcenter%252Findex.html%253Ffrom_tag%253Dqq%2526openid%253D&state=state&display=mobile&scope=get_user_info%2Cget_app_friends&pt_flex=1&loginfrom=&h5sig=eGKHXAcp1AAAlR38DBo6E_oj3OrsS53GtW1_bmkcOzY&loginty=3&'
                                    }
                                    ,
                                    allow_redirects=False,
                                    proxies=self.info.proxy_proxies)
            Location = response.headers['Location']
            if Location is None:
                return {'status': False, 'message': '没找到Location'}
            parsed_url = urlparse(Location)
            query_params = parse_qs(parsed_url.query)
            self.code = query_params.get('code')[0]
            if self.code is None:
                return {'status': False, 'message': '没找到code'}
            return {'status': True, 'code': self.code}
        except Exception as e:
            return {'status': False, 'message': f'获取code异常{e}'}

    def get_cookie(self):
        try:
            post_data = {
                "comm": {"ct": 23, "cv": 0, "g_tk": 5381, "platform": "h5"},
                "req": {
                    "module": "QQConnectLogin.LoginServer",
                    "method": "QQLogin",
                    "param": {"code": self.code}
                }
            }
            post_json = json.dumps(post_data)

            rsp = requests.post(
                url='https://u.y.qq.com/cgi-bin/musicu.fcg',
                data=post_json,
                allow_redirects=False,
                proxies=self.info.proxy_proxies
            )

            self.cookies = '; '.join([f'{c.name}={c.value}' for c in rsp.cookies])
            self.qm_keyst = re.search(r'qm_keyst=([^;]+)', self.cookies).group(1)
            self.g_tk = qq_bkn(self.qm_keyst)
            self.psrf_qqopenid = rsp.cookies.get('psrf_qqopenid')
            return {'status': True}
        except Exception as e:
            return {'status': False, 'message': f'获取cookie异常{e}'}

    def get_tasks(self):
        if not all([self.psrf_qqopenid, self.g_tk, self.qm_keyst]):
            return {'status': False, 'message': '获得任务参数不全。'}
        urls = ['https://u6.y.qq.com/cgi-bin/musicu.fcg', 'https://u6.y.qq.com/cgi-bin/musics.fcg']
        try:
            for url in urls:
                # url = "https://u6.y.qq.com/cgi-bin/musics.fcg"
                data = {
                    "comm": {
                        "g_tk": self.g_tk,
                        "uin": int(self.uin),
                        "format": "json",
                        "inCharset": "utf-8",
                        "outCharset": "utf-8",
                        "notice": 0,
                        "platform": "h5",
                        "needNewCode": 1
                    },
                    "req_0": {
                        "module": "music.activeCenter.ActiveCenterZoneSvr",
                        "method": "QQTrans",
                        "param": {
                            "openid": self.psrf_qqopenid
                        }
                    }
                }

                data = json.dumps(data, separators=(',', ':'))
                querystring = {"_webcgikey": "QQTrans",  # 任务名
                               "_": int(time.time() * 1000),
                               "sign": music_sign(data)}

                headers = {
                    "Host": "u6.y.qq.com",
                    "Accept": "application/json",
                    "Sec-Fetch-Site": "same-site",
                    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
                    "Sec-Fetch-Mode": "cors",
                    "Origin": "https://y.qq.com",
                    "User-Agent": User_Agent,
                    "Referer": "https://y.qq.com/",
                    "Sec-Fetch-Dest": "empty",
                    "Connection": "close",
                    "Cookie": self.cookies,
                    "Content-Type": "application/json"
                }

                response = requests.request("POST", url,
                                            params=querystring,
                                            data=data,
                                            headers=headers,
                                            proxies=self.info.proxy_proxies

                                            )

                code = response.json()['code']
                if code != 0:
                    return {'status': False, 'code': code, 'message': '获取任务失败'}
                return {'status': True, 'code': code, 'message': '获取任务失败'}


        except Exception as e:
            return {'status': False, 'message': f'获取任务异常{e}'}

    def play_music(self):
        succNum = 0
        try:
            for i in range(6):
                timestamp = str(int(time.time()))
                times = str(12 * 60)
                timeKey = hashlib.md5((timestamp + times + self.uin + "gk2$Lh-&l4#!4iow").encode()).hexdigest()
                xml = f'<?xml version="1.0" encoding="UTF-8"?><root><qq>{self.uin}</qq><authst>{self.qm_keyst}</authst><ct>11</ct><cv>12030508</cv><uid>5137010676</uid><item cmd="1" optime="{timestamp}" nettype="1030" QQ="{self.uin}" time="{times}" time2="657" timekey="{timeKey}" songid="108955211" singerid="4418" fversion="0"/></root>'
                gzip_buffer = BytesIO()
                with gzip.GzipFile(mode='wb', fileobj=gzip_buffer) as gzip_file:
                    gzip_file.write(xml.encode('utf-8'))
                compressed_xml = gzip_buffer.getvalue()

                response = requests.post(
                    url='https://stat.y.qq.com/android/fcgi-bin/imusic_tj',
                    headers={
                        'User-Agent': 'QQMusic 9020807(android 9)',
                        'Content-Encoding': 'gzip',
                    },
                    data=compressed_xml,
                    proxies=self.info.proxy_proxies

                )
                if response.status_code == 200:
                    body = response.content
                    if body and body[-1] == 0xD7:
                        succNum += 1
                if succNum >= 3:
                    break
            if succNum >= 3:
                return {'status': True, 'message': '播放成功'}
            else:
                return {'status': False, 'message': '播放失败'}

        except Exception as e:
            return {'status': False, 'message': f'播放异常:{e}'}

    def task(self):
        # 结束需要通过 获取账号页面确认
        for func in [self.get_Location_code, self.get_cookie, self.get_tasks, self.play_music]:
            rsp = func()
            if not rsp['status']:
                return rsp
        return rsp


if __name__ == '__main__':
    pass
    # music = Music()
    # print(music.task())
