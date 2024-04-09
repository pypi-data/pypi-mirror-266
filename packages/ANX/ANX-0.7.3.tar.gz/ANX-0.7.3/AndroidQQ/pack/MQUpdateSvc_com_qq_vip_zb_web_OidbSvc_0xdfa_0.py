from pyproto import ProtoBuf

from AndroidQQ.struct import PackHeadNoToken, Pack_


def OidbSvc_0xdfa_0(info):
    # buffer = ProtoBuf({2: 0,
    #                    3: '{"stsetgxhreq":{"appid":23,"itemid":0,"opplat":2,"qqver":"8.9.83","hashid":"D26F32B308A52FA81C0710010701ED17"},"cmd":6}'}).toBuf()

    buffer = bytes.fromhex('08 00 01 06 04 72 65 73 70 1D 00 00 39 0A 02 0D 80 F2 07 19 00 01 0A 02 0D 80 F2 07 1C 21 4D 57 3D 00 00 13 08 90 04 10 92 8F E6 DB 83 80 80 80 02 18 00 20 E0 86 03 4C 5C 6C 7C 8C 9C AC 0B 22 73 B0 95 09 4C 0B')

    buffer = PackHeadNoToken(info, buffer, 'OnlinePush.RespPush','OnlinePush','SvcRespPushMsg')
    buffer = Pack_(info, buffer, Types=11, encryption=1, sso_seq=info.seq)
    return buffer
