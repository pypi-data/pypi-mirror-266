from google.protobuf.json_format import MessageToDict

from AndroidQQ.im.oidb.cmd0xeb8 import ReqBody, RspBody
from AndroidQQ.im.oidb.oidb_sso import OIDBSSOPkg
from AndroidQQ.struct import PackHeadNoToken, Pack_


def OidbSvc_0xeb8(info):
    req_body = ReqBody(
        src=1,
        proto_ver=2
    )
    oIDBSSOPkg = OIDBSSOPkg(
        command=3768,
        service_type=1,
        bodybuffer=req_body.SerializeToString(),
    )
    buffer = oIDBSSOPkg.SerializeToString()
    # print(buffer.hex())
    buffer = PackHeadNoToken(info, buffer, 'OidbSvc.0xeb8')
    buffer = Pack_(info, buffer, Types=11, encryption=1, sso_seq=info.seq)
    return buffer


def OidbSvc_0xeb8_rep(buffer):
    oIDBSSOPkg = OIDBSSOPkg()
    oIDBSSOPkg.ParseFromString(buffer)
    rep_body = RspBody()
    rep_body.ParseFromString(oIDBSSOPkg.bodybuffer)
    return MessageToDict(rep_body)
