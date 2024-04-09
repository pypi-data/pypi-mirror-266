# struct com.tencent.mobileqq.troop.handler;
from google.protobuf.json_format import MessageToDict

from AndroidQQ.im.oidb.cmd0x88d.oidb_0x88d_pb2 import ReqGroupInfo, GroupInfo, ReqBody, RspBody
from AndroidQQ.im.oidb.oidb_sso import OIDBSSOPkg
from AndroidQQ.struct import Pack_Head, Pack_


def stgroupinfo():
    group_info = GroupInfo()
    group_info.group_class_ext = 0
    group_info.group_answer = ''
    return group_info


def OidbSvc_0x88d_1(info, group_code: int):
    group_info = GroupInfo(
        group_class_ext=0,
        group_answer=''
    )

    reqGroupInfo = ReqGroupInfo(
        group_code=group_code,
        stgroupinfo=group_info,

    )
    reqBody = ReqBody(
        appid=info.device.app_id,
        reqgroupinfo=[reqGroupInfo],
    )
    oIDBSSOPkg = OIDBSSOPkg(
        command=2189,
        service_type=1,  # 不等于 1 OidbSvc.0x88d_0
        bodybuffer=reqBody.SerializeToString(),
    )
    buffer = oIDBSSOPkg.SerializeToString()

    buffer = Pack_Head(info, buffer, 'OidbSvc.0x88d_1')
    buffer = Pack_(info, buffer, Types=8, encryption=1, token=True)
    return buffer


def OidbSvc_0x88d_1_rep(buffer):
    oIDBSSOPkg = OIDBSSOPkg()
    oIDBSSOPkg.ParseFromString(buffer)
    rep_body = RspBody()
    rep_body.ParseFromString(oIDBSSOPkg.bodybuffer)
    return MessageToDict(rep_body)


if __name__ == '__main__':
    pass
