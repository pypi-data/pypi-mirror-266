from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader
from .cmshow_active_result import cmshow_active_result


class operation_like_rsp(IJceStruct):
    ret: int = 0
    msg: str = ''
    cmshow_active_result: IJceStruct = None  # 厘米秀

    def read_from(self, reader: JceReader) -> None:
        self.ret = reader.read_any(0)
        self.msg = reader.read_any(1)
        self.cmshow_active_result = reader.read_object(cmshow_active_result)  # 厘米秀
    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
