from google.protobuf.json_format import MessageToDict

from AndroidQQ.im.oidb.oidb_0xc05 import *
from AndroidQQ.im.oidb.oidb_sso import OIDBSSOPkg
from AndroidQQ.struct import PackHeadNoToken, Pack_


def OidbSvc_0xc05(info, start: int, limit: int):
    getAuthAppListinfoReq = GetAuthAppListReq(
        start=start,
        limit=limit
    )
    req_body = ReqBody(
        get_auth_app_list_req=getAuthAppListinfoReq
    )
    oIDBSSOPkg = OIDBSSOPkg(
        command=3077,
        result=0,
        service_type=1,
        bodybuffer=req_body.SerializeToString(),
    )
    buffer = oIDBSSOPkg.SerializeToString()
    buffer = PackHeadNoToken(info, buffer, 'OidbSvc.0xc05')
    buffer = Pack_(info, buffer, Types=11, encryption=1, sso_seq=info.seq)
    return buffer


def OidbSvc_0xc05_rep(buffer):
    oIDBSSOPkg = OIDBSSOPkg()
    oIDBSSOPkg.ParseFromString(buffer)
    rep_body = RspBody()
    rep_body.ParseFromString(oIDBSSOPkg.bodybuffer)
    return MessageToDict(rep_body)
