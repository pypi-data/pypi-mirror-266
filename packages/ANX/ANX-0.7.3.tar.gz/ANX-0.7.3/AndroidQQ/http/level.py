import json
import re

import requests
from AndroidQQ.utils import qq_bkn
from bs4 import BeautifulSoup

from AndroidQQ import log

from .headers import *


def qq_level_index(info, cookie: str):
    """获取QQ等级的具体信息 多了需要代理"""
    try:
        response = requests.get(
            url="https://ti.qq.com/qqlevel/index",
            params={
                "_wv": "3",
                "_wwv": "1",
                "tab": "3",
                "source": "26",
            },
            headers={
                "Host": "ti.qq.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": User_Agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                          "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "X-Requested-With": "com.tencent.mobileqq",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            proxies=info.proxy_proxies
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')
        data_string = None
        for script in scripts:
            if script.string and '__INITIAL_STATE__' in script.string:
                data_string = script.string
                break

        # 提取JavaScript对象

        json_data = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', data_string).group(1)
        json_data = json.loads(json_data)
        return json_data

    except requests.exceptions.RequestException:
        log.error('HTTP 请求失败')
        return {}


def GetLevelTask(info, cookie):
    """获取任务,具有更新效果"""

    try:
        rsp = requests.post(

            url="https://ti.qq.com/qqlevel/trpc/levelTask/Get",
            params={
                "bkn": qq_bkn(info.cookies.skey),
            },

            json={
                "mode": 7
            },

            headers={
                "Host": "ti.qq.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": User_Agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                          "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "X-Requested-With": "com.tencent.mobileqq",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            proxies=info.proxy_proxies
        )
        return rsp.json()
    except Exception as e:
        log.error(f'获取等级任务列表失败{e}')
        return {}


def RefreshTask(info, cookie, task_id: str):
    """刷新任务"""
    try:
        rsp = requests.post(
            url="https://ti.qq.com/qqlevel/trpc/levelTask/Refresh",
            params={
                "bkn": qq_bkn(info.cookies.skey),
            },
            json={
                "task_id": task_id,
                "mode": 7

            },

            headers={
                "Host": "ti.qq.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": User_Agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                          "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "X-Requested-With": "com.tencent.mobileqq",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            proxies=info.proxy_proxies

        )
        return rsp.json()
    except Exception as e:
        log.error(f'刷新任务失败{e}')
        return {}


def format_conversion(data_json):
    """转换任务格式"""
    response = data_json.get('response')
    base_task_list = response.get('base_info', {}).get('base_task_list', [])
    extra_task_list = response.get('extra_info', {}).get('extra_task_list', [])
    base_task_list.extend(extra_task_list)
    task_list = {}
    done_count = 0
    for row in base_task_list:
        title = row['title']
        task_list[title] = {}
        task_list[title]['button_text'] = row['button_text']
        task_list[title]['is_done'] = row['is_done']
        task_list[title]['task_id'] = row['task_id']

        if row['is_done']:
            done_count = done_count + 1

    task_list['done_count'] = done_count

    keys_to_delete = [
        '会员极速星二阶专享',
        '会员极速星三阶专享',
        '会员极速星专享',
        '大会员-Thunder开通用户专享',
        'SVIP-STAR开通用户专享',
        'SVIP10三星+豪华黄钻LV10至尊版专享',
        'QQ大会员超级包月身份专享',
        'QQ大会员连续包月特权专享',
        '邀请好友助力',
        'SVIP连续包月特权',
        '电脑QQ在线',
        '参加龙王令活动获取加速天数',
        'SVIP连续包月特权',
    ]
    for key in keys_to_delete:
        task_list.pop(key, None)
    return task_list


def GetLevelStatus(info, cookie, query: bool = False):
    try:

        rsp = requests.post(
            url='https://ti.qq.com/qqlevel/trpc/levelTaskCenter/GetLevelStatus?bkn=' + qq_bkn(info.cookies.skey),
            headers={
                "Host": "ti.qq.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": User_Agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                          "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "X-Requested-With": "com.tencent.mobileqq",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            proxies=info.proxy_proxies

        )
        return format_conversion(rsp.json()) if query else rsp.json().get('response', {})
    except Exception as e:
        log.error(f'获取等级任务列表失败{e}')
        return {}


if __name__ == '__main__':
    # print(qq_level_index())
    pass
