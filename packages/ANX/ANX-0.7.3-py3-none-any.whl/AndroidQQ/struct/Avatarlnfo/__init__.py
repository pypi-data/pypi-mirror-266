from Jce_b import JceReader

from .QQHeadUrlResp import *
from .DestQQHeadInfo import *

from .QQHeadUrlReq import *
from .. import PackHeadNoToken, Pack_, Un_jce_Head


def GetAvatarInfo(info, **kwargs):
    """获取头像信息"""
    _DestInfo = DestQQHeadInfo(**kwargs)
    Buffer = QQHeadUrlReq(destUserInfo=[_DestInfo], **kwargs).writeTo()
    Buffer = JceWriter().write_jce_struct(Buffer, 0)
    Buffer = JceWriter().write_map({'QQHeadUrlReq': Buffer}, 0)
    Buffer = PackHeadNoToken(info, Buffer, 'AvatarInfoSvr.QQHeadUrlReq',
                             'GetAvatarInfo', 'QQHeadUrlReq')
    Buffer = Pack_(info, Buffer, Types=11, encryption=1, sso_seq=info.seq)
    return Buffer


def GetAvatarInfo_res(Buffer):
    """获取头像信息"""
    Buffer = Un_jce_Head(Buffer)
    _map = JceReader(Buffer).read_map(0)
    QQHeadUrlResp_Buffer = _map.get('QQHeadUrlResp', None)
    qq_head_url_resp = QQHeadUrlResp()
    qq_head_url_resp.read_from(JceReader(QQHeadUrlResp_Buffer))
    return qq_head_url_resp.to_dict()
