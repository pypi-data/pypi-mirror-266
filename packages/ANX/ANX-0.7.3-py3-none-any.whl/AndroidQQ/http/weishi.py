import json
import requests

from AndroidQQ.http import User_Agent
from AndroidQQ.http.ClientKey import ClientKeyToCookies


def weishi_up_(info):
    if not info.cookies.client_key:
        return {'status': False, 'message': '没有获取到clientkey'}

    rsp = ClientKeyToCookies(info, info.uin, info.cookies.client_key)
    if not rsp['status']:
        return rsp
    try:
        cookies = rsp['cookie']
        params = {
            "req_body": {
                "blockID": "2",
                "bizPayload": "{\"taskId\":\"\"}"
            }
        }
        params = json.dumps(params)

        rsp = requests.post(
            url='https://api.weishi.qq.com/trpc.weishi.weishi_h5_proxy.weishi_h5_proxy/WelfareBlockObtain',
            params=params,
            headers={
                "User-Agent": User_Agent,
                "Content-Type": "multipart/form-data",
                "Origin": "https://isee.weishi.qq.com",
                "Referer": "https://isee.weishi.qq.com/",
                "Cookie": cookies,
                "wesee_fe_map_ext": "{}",
            },
            proxies=info.proxy_proxies

        )
        return {'status': True, 'rsp': rsp.json()}
    except Exception as e:
        return {'status': False, 'message': f'微视任务失败{e}'}


if __name__ == '__main__':
    pass
