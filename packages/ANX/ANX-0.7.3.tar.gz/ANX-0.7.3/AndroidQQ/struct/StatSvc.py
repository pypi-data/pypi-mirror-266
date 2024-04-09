import json
import zlib

from Jce import JceInputStream, JceStruct

from AndroidQQ.struct.head import *


def DelDevLoginInfo(info, **kwargs):
    """删除登录信息"""
    key = kwargs.get('key', b'')
    if isinstance(key, str):
        key = bytes.fromhex(key)

    _data = JceWriter().write_bytes(key, 0)

    jce = JceWriter()
    jce.write_bytes(info.Guid, 0)
    jce.write_string('com.tencent.mobileqq', 1)
    jce.write_jce_struct_list([_data], 2)
    jce.write_int32(1, 3)
    jce.write_int32(0, 4)
    jce.write_int32(0, 5)
    _data = jce.bytes()
    _data = JceWriter().write_jce_struct(_data, 0)
    _data = JceWriter().write_map({'SvcReqDelLoginInfo': _data}, 0)
    _data = PackHeadNoToken(info, _data, 'StatSvc.DelDevLoginInfo', 'StatSvc', 'SvcReqDelLoginInfo')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def DelDevLoginInfo_res(data):
    """似乎没有明确的返回信息"""
    data = Un_jce_Head(data)
    data = Un_jce_Head_2(data)
    stream = JceInputStream(data)
    jce = JceStruct()
    jce.read_from(stream)
    return jce.to_json()
