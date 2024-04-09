# friendlist 好友列表
from Jce import JceInputStream, JceStruct
from Jce_b import JceWriter

from AndroidQQ.struct import PackHeadNoToken, Pack_, Un_jce_Head, Un_jce_Head_2


def GetSimpleOnlineFriendInfoReq(info=None, **kwargs):
    """"获取简单好友列表"""
    jce = JceWriter()
    jce.write_int64(int(info.uin), 0)
    jce.write_bool(kwargs.get('ifgetFriendVideoAbi', False), 1)  # 是否获取朋友的视频能力
    jce.write_bool(kwargs.get('isReqCheckIn', False), 2)  # 是否请求签到
    jce.write_bool(kwargs.get('ifShowTermType', True), 4)  # 是否显示好友的设备类型
    jce.write_int32(kwargs.get('version', 33), 5)  # 版本号
    jce.write_int32(kwargs.get('cSrcType', 1), 6)  # 来源类型
    _data = jce.bytes()
    _data = JceWriter().write_jce_struct(_data, 0)
    _data = JceWriter().write_map({'FSOLREQ': _data}, 0)
    _data = PackHeadNoToken(info, _data, 'friendlist.GetSimpleOnlineFriendInfoReq',
                            'mqq.IMService.FriendListServiceServantObj', 'GetSimpleOnlineFriendInfoReq')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def GetSimpleOnlineFriendInfoReq_res(data):
    """获取简单好友列表"""
    data = Un_jce_Head(data)
    data = data[18:]
    stream = JceInputStream(data)
    jce = JceStruct()
    jce.read_from(stream)
    return jce.to_json()
