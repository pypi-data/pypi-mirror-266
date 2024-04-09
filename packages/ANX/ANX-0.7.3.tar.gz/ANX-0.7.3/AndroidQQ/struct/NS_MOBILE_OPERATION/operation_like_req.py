# package NS_MOBILE_OPERATION;
from typing import Any, Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class operation_like_req(IJceStruct):
    action: int = 0
    appid: int = 0
    busi_param: dict = None
    bypass_param: dict = None
    bypass_param_binary: bytes = None
    curkey: str = ""
    extern_param: dict = None
    hostuin: int = 0
    uin: int = 0
    unikey: str = ""

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        jce = JceWriter()
        jce.write_object(self.uin, 0)
        if self.curkey is not None:
            jce.write_object(self.curkey, 1)

        if self.unikey is not None:
            jce.write_object(self.unikey, 2)

        jce.write_object(self.action, 3)
        jce.write_object(self.appid, 4)
        if self.busi_param is not None:
            jce.write_map(self.busi_param, 5)

        jce.write_object(self.hostuin, 6)

        if self.extern_param is not None:
            jce.write_object(self.extern_param, 7)
        if self.bypass_param is not None:
            jce.write_object(self.bypass_param, 8)
        if self.bypass_param_binary is not None:
            jce.write_object(self.bypass_param_binary, 9)

        return jce.bytes()
