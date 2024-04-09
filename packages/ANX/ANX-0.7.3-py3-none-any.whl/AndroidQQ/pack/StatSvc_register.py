from Jce_b import JceWriter, JceReader

from AndroidQQ.struct import Pack_, Pack_Head, Un_jce_Head, Un_jce_Head_2
from AndroidQQ.struct.push.SvcRespRegister import SvcRespRegister


def StatSvc_register(info, Buffer):
    """
        :param info:
        :param Buffer:
        :return:
    """
    Buffer = JceWriter().write_jce_struct(Buffer, 0)

    Buffer = JceWriter().write_map({'SvcReqRegister': Buffer}, 0)
    jce = JceWriter()
    jce.write_int32(3, 1)
    jce.write_int32(0, 2)
    jce.write_int32(0, 3)
    jce.write_int64(0, 4)
    jce.write_string('PushService', 5)
    jce.write_string('SvcReqRegister', 6)
    jce.write_bytes(Buffer, 7)
    jce.write_int32(0, 8)
    Buffer = jce.bytes()
    Buffer = Buffer + bytes.fromhex('98 0C A8 0C')  # 后面的两个空的
    Buffer = Pack_Head(info, Buffer, 'StatSvc.register')
    Buffer = Pack_(info, Buffer, Types=10, encryption=1, token=True)
    return Buffer


def StatSvc_register_rsp(Buffer):
    Buffer = Un_jce_Head(Buffer)
    Buffer = Un_jce_Head_2(Buffer)
    result = JceReader(Buffer).read_object(SvcRespRegister).to_dict()
    return result
