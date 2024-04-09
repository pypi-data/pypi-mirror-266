import time
from urllib.parse import urlparse, parse_qs

import requests
from box import Box

from AndroidQQ.http import User_Agent


class credit_score:

    def __init__(self, info, clientkey):
        # self.uin = '3484129139'
        # self.clientkey = '9f2677a5c3c9dd3571f4c14c3a796f06cd54ade8e7983f68b2e8bdb557e65eabc849b9b87cf8a6ed69f2a3e4b99d2dde'
        #
        self.gs_code = None
        self.uin = info.uin
        self.clientkey = clientkey
        self.get_gs_code()
        self.info = info

    def get_gs_code(self):
        try:
            response = requests.get(url="https://ssl.ptlogin2.qq.com/jump",
                                    params={
                                        "keyindex": "19",
                                        "clientuin": self.uin,
                                        "clientkey": self.clientkey,
                                        "u1": "https://connect.qq.com",
                                        "pt_report": "1",
                                        "pt_aid": "716027609",
                                        "daid": "383",
                                        "style": "35",
                                        "pt_ua": "B0BFB00844CA89BF32B35D60533238A2",
                                        "pt_browser": "Chrome",
                                        "pt_3rd_aid": "102053620",
                                        "pt_openlogin_data": f"appid=716027609&pt_3rd_aid=102053620&daid=383&pt_skey_valid=0&style=35&s_url=https%3A%2F%2Fconnect.qq.com&refer_cgi=authorize&which=&sdkp=pcweb&sdkv=v1.0&time={str(int(time.time()))}&loginty=3&h5sig=G_tqev5eSttaANNnVgcw5gCN25vuzK7ef9fUPcYGmUY&state=qqconnect_1&client_id=102053620&response_type=code&scope=all&redirect_uri=https%3A%2F%2Fgamecredit.qq.com%2Flogin-ui%2Findex.html%3FcPageName%3Dmiddle%26type%3DQQ%26backUrl%3Dreload%26appId%3D102053620&pt_flex=1&loginfrom=&h5sig=G_tqev5eSttaANNnVgcw5gCN25vuzK7ef9fUPcYGmUY&loginty=3&",
                                    }
                                    ,
                                    allow_redirects=False,
                                    proxies=self.info.proxy_proxies)
            Location = response.headers['Location']

            if Location is None:
                return {'status': False, 'message': '没找到Location'}
            parsed_url = urlparse(Location)
            query_params = parse_qs(parsed_url.query)
            code = query_params.get('code')[0]
            response = requests.get(url=f'https://gamecredit.qq.com/connect?code={code}&appId=102053620&atype=QQ',
                                    allow_redirects=False,
                                    proxies=self.info.proxy_proxies
                                    )
            self.gs_code = response.cookies.get('gs_code')
            if self.gs_code is None:
                return {'status': False, 'message': '没找到gs_code'}
            return {'status': True, 'cookie': self.gs_code}
        except Exception as e:
            return {'status': False, 'message': f'获取gs_code异常:{e}'}

    def query_common_credit(self):
        if not self.gs_code:
            return {'status': False, 'message': 'gs_code为空', 'score': 0}

        try:
            response = requests.get(
                url="https://gamecredit.qq.com/api/qq/proxy/query_common_credit",
                headers={
                    "Host": "gamecredit.qq.com",
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "sec-ch-ua-mobile": "?0",
                    "User-Agent": User_Agent,
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://gamecredit.qq.com/static/web/index.html",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cookie": "gs_code=" + self.gs_code,
                },
                proxies=self.info.proxy_proxies
            )
            data = response.json().get('data', {})
            score = data.get('score', -1)
            return {'status': True, 'score': score, 'data': data}
        except requests.exceptions.RequestException:
            return {'status': False, 'score': 0, 'message': '请求失败'}


if __name__ == '__main__':
    pass
    # print(credit_score().query_common_credit())
    # query_common_credit()
#
# ptui_qlogin()

# send_request()
# connect()

# query_common_credit()
