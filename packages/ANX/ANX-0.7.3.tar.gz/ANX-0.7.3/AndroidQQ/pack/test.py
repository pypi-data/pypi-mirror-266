from AndroidQQ.struct import Pack_, Pack_Head, PackHeadNoToken


def avatar_test(info):
    """
    """
    buffer = bytes.fromhex(
        '08 00 01 06 04 72 65 73 70 1D 00 00 39 0A 02 57 20 27 53 19 00 01 0A 02 57 20 27 53 1C 21 D4 A3 3D 00 00 13 08 90 04 10 FD CF A1 EC 86 80 80 80 02 18 00 20 DB 86 03 4C 5C 6C 7C 8C 9C AC 0B 22 E5 95 95 0B 4C 0B ')
    buffer = PackHeadNoToken(info, buffer, 'OnlinePush.RespPush','OnlinePush','SvcRespPushMsg')
    buffer = Pack_(info, buffer, Types=11, encryption=1, sso_seq=info.seq)
    return buffer
