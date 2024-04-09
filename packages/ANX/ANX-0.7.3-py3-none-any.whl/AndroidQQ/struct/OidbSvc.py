import json
# 对象数据服务
from google.protobuf.json_format import MessageToJson, MessageToDict

from AndroidQQ.proto import *
from AndroidQQ.struct.head import *
from pyproto import ProtoBuf


def P0xccd(info, **kwargs):
    """删除授权信息"""
    _dict = {1: 3277, 2: 1, 3: 0, 4: {2: kwargs.get('appid', 0), 3: 1}}
    _data = ProtoBuf(_dict).toBuf()
    _data = PackHeadNoToken(info, _data, 'OidbSvc.0xccd')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def P0xccd_res(data):
    _dict = ProtoBuf(data).toDictAuto()
    return _dict
