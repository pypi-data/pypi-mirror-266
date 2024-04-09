# 消息服务
from Jce import JceInputStream, JceStruct
from Jce_b import JceWriter

from AndroidQQ.struct import PackHeadNoToken, Pack_, Un_jce_Head, Un_jce_Head_2


def PullUnreadMsgCount(info):
    """拉取未读消息数"""
    jce = JceWriter()
    jce.write_int32(1, 0)
    jce.write_int32(1, 1)
    jce.write_int32(1, 2)
    _data = jce.bytes()
    _data = JceWriter().write_jce_struct(_data, 0)
    _data = JceWriter().write_map({'req_PullUnreadMsgCount': _data}, 0)
    _data = PackHeadNoToken(info, _data, 'MessageSvc.PullUnreadMsgCount', 'MessageSvc', 'PullUnreadMsgCount')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def PullUnreadMsgCount_res(data):
    """2=未读消息数"""
    data = Un_jce_Head(data)
    data = data[32:]  # 去掉头部
    jce = JceStruct()
    jce.read_from(JceInputStream(data))
    return jce.to_json()
