import time

import requests
from box import Box

from AndroidQQ.http import User_Agent

bot_uin = [66600000, 2854196306, 2854213893, 2854211892, 2854204259]


# 66600000 2854196306 2854213893 2854211892 2854204259

def delete_qq_friend(info, uin, fuin, bkn, cookie):
    """空间包删除好友"""

    try:
        rsp = requests.post(
            url='https://h5.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/tfriend/friend_delete_qqfriend.cgi?g_tk=' + bkn,
            data={
                'uin': uin,
                'fupdate': '1',
                'num': '1',
                'fuin': fuin,
                'format': 'json',
                'qzreferrer': f'http://user.qzone.qq.com/{uin}/myhome/friends'
            },
            headers={
                "User-Agent": User_Agent,
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://h5.qzone.qq.com",
                "Referer": "https://h5.qzone.qq.com/",
                'Cookie': cookie,

            },
            proxies=info.proxy_proxies
        )
        return Box(status=True, message=f'空间请求删除好友', echo=rsp.json())
    except Exception as e:
        return Box(status=False, message=f'空间删除好友异常{e}')


class Friends:
    def __init__(self, info, bkn, uin, cookie):
        self.info = info
        self.bkn = bkn
        self.uin = uin
        self.cookie = cookie
        pass

    def add_friend(self, robot_uin):
        try:
            rsp = requests.post(url='https://qun.qq.com/cgi-bin/qunapp/robots_addfriend?bkn=' + self.bkn,
                                data={
                                    'robot_uin': robot_uin,
                                    'bkn': self.bkn
                                },
                                headers={
                                    "User-Agent": User_Agent,
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Origin": "https://web.qun.qq.com",
                                    "X-Requested-With": "com.tencent.mobileqq",
                                    "Referer": "https://web.qun.qq.com/",
                                    "Cookie": self.cookie
                                },
                                proxies=self.info.proxy_proxies
                                )

            return Box(status=True, message=f'已请求添加好友', echo=rsp.json())

        except Exception as e:
            return Box(status=False, message=f'添加好友异常{e}')

    def del_friend(self, robot_uin):
        """删除好友"""
        try:
            rsp = requests.post(url='https://qun.qq.com/cgi-bin/qunapp/robots_removefriend?bkn=' + self.bkn,
                                data={
                                    'robot_uin': robot_uin,
                                    'bkn': self.bkn
                                },
                                headers={
                                    "User-Agent": User_Agent,
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Origin": "https://web.qun.qq.com",
                                    "X-Requested-With": "com.tencent.mobileqq",
                                    "Referer": "https://web.qun.qq.com/",
                                    "Cookie": self.cookie
                                },
                                proxies=self.info.proxy_proxies
                                )

            return Box(status=True, message=f'已申请删除好友', echo=rsp.json())

        except Exception as e:
            return Box(status=False, message=f'删除好友异常{e}')


if __name__ == '__main__':
    print(Friends().add_friend(2854211892))
    # delete_qq_friend(2854211892, '795050525',
    #                  'uin=o1151930580; skey=MUDOsUo5A6; p_uin=o1151930580; p_skey=NL0sm39T2*NRDOc-I8J*BM6KuHKL8xSZqjYEwVVXGzM_;')

    # print(Friends().del_friend(2854211892))
    pass
