from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class operation_publishmood_rsp(IJceStruct):
    msg: str = ""
    ret: int = 0
    tid: str = ""
    verifyurl: str = ""  # 验证者

    def read_from(self, reader: JceReader) -> None:
        self.ret = reader.read_any(0)
        self.verifyurl = reader.read_any(1)
        self.tid = reader.read_any(2)
        self.msg = reader.read_any(3)

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
