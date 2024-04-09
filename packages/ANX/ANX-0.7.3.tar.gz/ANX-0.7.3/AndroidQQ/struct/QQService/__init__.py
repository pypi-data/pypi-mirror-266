import zlib

from Jce import JceInputStream, JceStruct

from .SvcReqGetDevLoginInfo import *
from .. import PackHeadNoToken, Pack_, Un_jce_Head, Un_jce_Head_2


def GetDevLoginInfo_profile(info, item: SvcReqGetDevLoginInfo):
    """获取设备登录信息"""
    _buffer = item.to_bytes()
    _buffer = JceWriter().write_jce_struct(_buffer, 0)
    _buffer = JceWriter().write_map({'SvcReqGetDevLoginInfo': _buffer}, 0)
    _buffer = PackHeadNoToken(info, _buffer, 'StatSvc.GetDevLoginInfo', 'StatSvc', 'SvcReqGetDevLoginInfo')
    _buffer = Pack_(info, _buffer, Types=11, encryption=1, sso_seq=info.seq)
    return _buffer


def GetDevLoginInfo_res(data):
    if data[0] == 120:
        data = zlib.decompress(data)
    data = Un_jce_Head(data)
    data = Un_jce_Head_2(data)
    stream = JceInputStream(data)
    s = JceStruct()
    s.read_from(stream)
    return s.to_json()
