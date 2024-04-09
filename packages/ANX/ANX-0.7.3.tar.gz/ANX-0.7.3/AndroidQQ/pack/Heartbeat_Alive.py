from loguru import logger

from AndroidQQ.struct import PackHeadNoToken, Pack_


def Heartbeat_Alive(info):
    """快速网络检测Heartbeat """
    # todo 暂未完成
    buffer = PackHeadNoToken(info, b'', 'Heartbeat.Alive')
    buffer = Pack_(info, buffer, Types=11, encryption=1, sso_seq=info.seq)
    return buffer


def Heartbeat_Alive_rsp(Buffer: bytes):
    logger.info(Buffer.hex())
