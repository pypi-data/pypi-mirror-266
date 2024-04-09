import time

import requests


def ClientKeyToCookies(info, uin, client_key):
    try:
        response = requests.get(url="https://ssl.ptlogin2.qq.com/jump",
                                params={
                                    "keyindex": "19",
                                    "clientuin": uin,
                                    "clientkey": client_key,
                                    "u1": "https://connect.qq.com",
                                    "pt_report": "1",
                                    "pt_aid": "716027609",
                                    "daid": "383",
                                    "style": "35",
                                    "pt_ua": "60C3D6175A88C661094CF87DC58D1C55",
                                    "pt_browser": "others",
                                    "pt_3rd_aid": "1101083114",
                                    "pt_openlogin_data": f"appid=716027609&pt_3rd_aid=1101083114&daid=383&pt_skey_valid=0&style=35&s_url=https%3A%2F%2Fconnect.qq.com&refer_cgi=authorize&which=&sdkp=pcweb&sdkv=v1.0&time={str(int(time.time()))}&loginty=3&h5sig=OnX6dkcSfE3T5i4O7UxIp2gnmDJnviaXNxQcfA9X1Xg&response_type=code&client_id=1101083114&redirect_uri=https%3A%2F%2Fh5.weishi.qq.com%2Fweishi%2Faccount%2Flogin%3Fr_url%3Dhttp%253A%252F%252Fmedia.weishi.qq.com%252F%26loginfrom%3Dqc%26retry%3D1&state=state&pt_flex=1&loginfrom=&h5sig=OnX6dkcSfE3T5i4O7UxIp2gnmDJnviaXNxQcfA9X1Xg&loginty=3&",
                                }
                                ,
                                allow_redirects=False,
                                proxies=info.proxy_proxies
                                )
        Location = response.headers['Location']
        if Location is None:
            return {'status': False, 'message': '没找到Location'}
        response = requests.get(url=Location, allow_redirects=False, proxies=info.proxy_proxies
                                )
        cookie_str = '; '.join([f'{c.name}={c.value}' for c in response.cookies])

        return {'status': True, 'cookie': cookie_str}
    except Exception as e:
        return {'status': False, 'message': f'ClientKeyToCookies获取cookie异常:{e}'}
