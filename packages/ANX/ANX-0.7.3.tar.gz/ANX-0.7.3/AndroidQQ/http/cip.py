import requests
from bs4 import BeautifulSoup


def parse_proxy_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    div_tag = soup.find('div', class_='data kq-well')
    if div_tag:
        pre_tag = div_tag.find('pre')
        if pre_tag:
            pre_text = pre_tag.get_text()
            return pre_text
        else:
            return None
    else:
        return None


def GetHttpIp(info):
    """获取http代理ip"""
    try:
        rsp = requests.get('https://cip.cc',
                           timeout=5,
                           proxies=info.proxy_proxies
                           )
        proxy_info = parse_proxy_info(rsp.content)
        if proxy_info:
            return proxy_info
        else:
            return None
    except Exception as e:
        return None
