import json
from random import randint

from AndTools import pack_b, get_random_bin, TEA
from Jce_b import JceWriter, JceReader
from pyproto import ProtoBuf

from AndroidQQ import log


def Pack_(info, data, Types, encryption, sso_seq=None, token=False):
    """组包
    Types:包类型  通常是10 和11
    encryption  加密方式   2 不需要token  1需要token
    sso_seq 包序号
    """
    Pack = pack_b()
    Pack.add_int(Types)
    Pack.add_bytes(encryption)
    if not info.uin:
        Uin_bytes = bytes.fromhex('30')
    else:
        Uin_bytes = info.uin.encode('utf-8')

    if token:
        D2 = info.UN_Tlv_list.D2_T143
        Pack.add_int(len(D2) + 4)
        Pack.add_bin(D2)

    if sso_seq is not None:
        Pack.add_int(sso_seq)
    Pack.add_bytes(0)

    Pack.add_int(len(Uin_bytes) + 4)
    Pack.add_bin(Uin_bytes)
    Pack.add_bin(data)
    bytes_temp = Pack.get_bytes()

    Pack.empty()
    Pack.add_int(len(bytes_temp) + 4)
    Pack.add_bin(bytes_temp)
    return Pack.get_bytes()


def Pack_Head(info, data, Cmd):
    """包头"""
    TokenA4 = info.UN_Tlv_list.TGT_T10A
    if TokenA4 is None:
        TokenA4 = b''

    Pack = pack_b()
    Pack.add_int(info.seq)
    Pack.add_int(info.device.app_id)
    Pack.add_int(info.device.app_id)

    Pack.add_Hex('01 00 00 00')
    Pack.add_Hex('00 00 00 00')
    Pack.add_Hex('00 00 01 00')
    Pack.add_int(len(TokenA4) + 4)
    Pack.add_bin(TokenA4)
    Pack.add_int(len(Cmd) + 4)
    Pack.add_bin(bytes(Cmd, 'utf-8'))
    Pack.add_Hex('00 00 00 08')
    Pack.add_bin(get_random_bin(4))

    Pack.add_body(info.device.Imei, 4, add_len=4)
    Pack.add_Hex('00 00 00 04')

    Pack.add_body(info.device.var, 2, add_len=2)

    bytes_temp = Pack.get_bytes()

    Pack.empty()
    Pack.add_int(len(bytes_temp) + 4)
    Pack.add_bin(bytes_temp)
    bytes_temp = Pack.get_bytes()

    Pack.empty()
    Pack.add_bin(bytes_temp)
    Pack.add_int(len(data) + 4)
    Pack.add_bin(data)
    bytes_temp = Pack.get_bytes()
    bytes_temp = TEA.encrypt(bytes_temp, info.share_key)
    return bytes_temp


def Pack_Head_login_test(info, Cmd, data_02):
    """返回前面的头,后面的单独写在组包的函数里面
    01 8C
    1F 41
    08 12
    """
    pack = pack_b()
    pack.add_int(info.seq)
    pack.add_int(info.device.app_id)
    pack.add_int(info.device.app_id)
    pack.add_Hex('01 00 00 00 00 00 00 00 00 00 03 00')
    pack.add_int(len(info.UN_Tlv_list.T10A_token_A4) + 4)
    pack.add_bin(info.UN_Tlv_list.T10A_token_A4)
    pack.add_int(len(Cmd.encode('utf-8')) + 4)
    pack.add_bin(Cmd.encode('utf-8'))

    pack.add_Hex('00 00 00 08')
    pack.add_bin(get_random_bin(4))

    pack.add_int(len(info.device.IMEI) + 4)
    pack.add_bin(info.device.IMEI)

    pack.add_Hex('00 00 00 04')

    pack.add_int(len(info.device.var) + 2, 2)
    pack.add_bin(info.device.var)

    # 增加的
    _dict = {9: 1, 11: 2052, 12: '08c7f955ce81db0cca48bca510001751740b', 14: 0, 16: '', 18: 0, 19: 1, 20: 1, 21: 0,
             23: {1: 'client_conn_seq', 2: '1691763088'},
             24: {1: bytes.fromhex(
                 '0C0B2A074B060DD4D8EA163940EE2E66347704F2157B4A556F283E0671E4E33796ABEE4DF07BC5B8DB14DFA63CFAF1F66483C729DCC38EF9F7DE844FE9D9A30B'),
                 2: 'fDjMVp3pEqXt',
                 3: {2: 'V1_AND_SQ_8.9.71_4332_YYB_D',
                     3: 'X_LuHJtftAAPTwFk9SOftIHXmx2mCAL19e+MiYSrIXopqlBkJKOqC9fu2qT0j1lmIy/f7TAWpLSZclldF6w8JzWj6vYSqzd9s='}},
             26: 100, 28: 2}

    data_temp = ProtoBuf(_dict).toBuf()

    pack.add_int(len(data_temp) + 4)
    pack.add_bin(data_temp)
    bytes_temp = pack.get_bytes()

    pack.empty()
    pack.add_int(len(bytes_temp) + 4)
    pack.add_bin(bytes_temp)

    data_head = pack.get_bytes()

    pack.empty()
    pack.add_int(len(data_02) + 4)
    pack.add_bin(data_02)
    data_02 = pack.get_bytes()

    data = data_head + data_02
    # 02
    # 01 8C

    data = TEA.encrypt(data, '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')

    return data


def Pack_Head_login(info, Cmd, Buffer):
    """返回前面的头,后面的单独写在组包的函数里面
    01 8C
    1F 41
    08 12
    """
    pack = pack_b()
    pack.add_int(info.seq)
    pack.add_int(info.device.app_id)
    pack.add_int(info.device.app_id)
    pack.add_Hex('01 00 00 00 00 00 00 00 00 00 01 00')
    pack.add_body(info.UN_Tlv_list.TGT_T10A, 4, add_len=4)
    pack.add_body(Cmd, 4, add_len=4)
    pack.add_body(get_random_bin(4), length=4, add_len=4)  # MsgCookies
    pack.add_body(info.device.Imei, 4, add_len=4)
    pack.add_Hex('00 00 00 04')
    pack.add_body(info.device.var, 2, add_len=2)
    bytes_temp = pack.get_bytes()

    pack.empty()
    pack.add_body(bytes_temp, 4, add_len=4)
    pack.add_body(Buffer, 4, add_len=4)
    data = pack.get_bytes()
    data = TEA.encrypt(data, '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
    return data


def PackHeadNoToken(info, sBuffer, serviceCmd, sServantName=None, sFuncName=None):
    """照抄的旧源码"""
    # struct com.qq.taf;

    if sServantName is not None:
        """jce部分"""
        iRequestId = randint(110000000, 999999999)
        jce = JceWriter()
        jce.write_int32(3, 1)  # iVersion
        jce.write_int32(0, 2)  # cPacketType
        jce.write_int32(0, 3)  # iMessageType
        jce.write_int64(iRequestId, 4)
        jce.write_string(sServantName, 5)
        jce.write_string(sFuncName, 6)
        jce.write_bytes(sBuffer, 7)
        jce.write_int32(0, 8)  # iTimeout
        _data = jce.bytes()
        _data = _data + bytes.fromhex('98 0C A8 0C')  # 后面的两个空的
    else:
        _data = sBuffer

    pack = pack_b()
    pack.add_int(len(serviceCmd) + 4)
    pack.add_bin(bytes(serviceCmd, 'utf-8'))
    pack.add_Hex('00 00 00 08')
    pack.add_bin(get_random_bin(4))
    pack.add_Hex('00 00 00 04')
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_int(len(_data_temp) + 4)
    pack.add_bin(_data_temp)
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_bin(_data_temp)
    pack.add_int(len(_data) + 4)
    pack.add_bin(_data)
    _data = pack.get_bytes()
    _data = TEA.encrypt(_data, info.share_key)

    return _data


def PackHead_QMF(info, serviceCmd, Upstream):
    """缝补补,又一年"""
    pack = pack_b()
    pack.add_int(len(serviceCmd) + 4)
    pack.add_bin(bytes(serviceCmd, 'utf-8'))
    pack.add_Hex('00 00 00 08')
    pack.add_bin(get_random_bin(4))
    pack.add_Hex('00 00 00 04')
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_int(len(_data_temp) + 4)
    pack.add_bin(_data_temp)
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_bin(_data_temp)
    pack.add_int(len(Upstream) + 4)
    pack.add_bin(Upstream)
    _data = pack.get_bytes()

    Buffer = TEA.encrypt(_data, info.share_key)

    Buffer = Pack_(info, Buffer, Types=11, encryption=1, sso_seq=info.seq)

    return Buffer


def Un_jce_Head(data) -> bytes:
    jce = JceReader(data)
    jce.read_int32(1)
    jce.read_int32(2)
    jce.read_int32(3)
    jce.read_int64(4)
    jce.read_string(5)
    jce.read_string(6)
    data = jce.read_any(7)
    return data


def Un_jce_Head_2(data) -> bytes:
    """Map"""
    jce = JceReader(data)
    jce.skip(1)  # ReadType
    jce.skip(2)  # ReadShort
    jce.read_string(0)
    jce.skip(1)  # ReadType
    jce.skip(2)  # ReadShort
    jce.read_string(0)
    data = jce.read_any(1)

    return data
