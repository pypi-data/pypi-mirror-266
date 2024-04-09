import json

import requests
from AndTools import TEA
from Jce import jce_to_json

from AndroidQQ.struct import Un_jce_Head


def get_sso_list():
    """获取服务器列表
    1 = host
    2 = port
    5 =protocol
    8 =city
    9 =country
    """

    response = requests.request(
        "POST",
        "https://configsvr.msf.3g.qq.com/configsvr/serverlist.jsp",
        data=bytes.fromhex(
            '97 DC AD 09 6E FC 50 91 C7 7D 0A D2 8F D9 45 A6 93 8E F3 C5 7A 44 CD BC 39 36 4D EA B1 C8 C5 50 40 88 0C 75 DA 15 37 56 A1 CA 14 1E 9B EE 2E CC 34 BF 63 13 68 13 F4 01 7B 0A 76 29 C5 40 D6 04 BB 0C 73 46 15 FA C3 F9 96 B0 AA F4 83 25 7E E7 8D 71 E1 4D 94 1E 9E 7A D8 93 EE 98 FF A8 61 0C 71 57 B7 2F 28 3A 15 63 9A CE 0F B4 BA 2E 8B 15 25 5C 7C BA 73 CC 1E 82')
    )
    if response.content:
        _data = TEA.decrypt(response.content, 'F0 44 1F 5F F4 2D A5 8F DC F7 94 9A BA 62 D4 11')
        _data = Un_jce_Head(_data[4:])
        _data = _data[27:]
        json_data = json.loads(jce_to_json(_data))
        ip_list = json_data['2']
        # print(ip_list)
        filtered_list = [x for x in ip_list if x['1'] != 'msfwifi.3g.qq.com' and x['8'] != 'sh']

        # msfwifi.3g.qq.com 同一个ip连接多了会被拒绝连接,因此删掉
        # 过滤掉上海
        return filtered_list  # 移动ip


if __name__ == '__main__':
    print(get_sso_list())
