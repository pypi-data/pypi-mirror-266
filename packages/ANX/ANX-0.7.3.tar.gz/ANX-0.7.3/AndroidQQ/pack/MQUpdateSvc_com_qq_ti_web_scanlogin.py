import json

from AndroidQQ.im.oidb.scanlogin import ScanLoginReq, ScanLoginRsp
from AndroidQQ.struct import PackHeadNoToken, Pack_


def web_scanlogin(info, service_type: int, token: str):
    """
        uint32_service_type int 4 扫码 5 确认登录
        bytes_token str

    """

    token = {
        'uint32_service_type': service_type,
        'bytes_token': token
    }
    scan_login_req = ScanLoginReq(
        service_type=0,
        token=json.dumps(token).encode('utf-8')
    )
    buffer = scan_login_req.SerializeToString()
    buffer = PackHeadNoToken(info, buffer, 'MQUpdateSvc_com_qq_ti.web.scanlogin')
    buffer = Pack_(info, buffer, Types=11, encryption=1, sso_seq=info.seq)
    return buffer


def web_scanlogin_req(buffer):
    scan_login_rsp = ScanLoginRsp()
    scan_login_rsp.ParseFromString(buffer)
    return scan_login_rsp.field4.decode()
