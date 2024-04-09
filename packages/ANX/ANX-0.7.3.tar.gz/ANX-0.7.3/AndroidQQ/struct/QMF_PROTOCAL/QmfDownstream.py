# package QMF_PROTOCAL;
from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class QmfDownstream(IJceStruct):
    BizCode: int = None
    BusiBuff: bytes = None
    Extra: bytes = None
    Seq: int = None
    ServiceCmd: str = None
    Uin: int = None
    WnsCode: int = None

    def read_from(self, reader: JceReader):
        self.Seq = reader.read_any(0)
        self.Uin = reader.read_any(1)
        self.WnsCode = reader.read_any(2)
        self.BizCode = reader.read_any(3)
        self.ServiceCmd = reader.read_any(4)
        self.BusiBuff = reader.read_any(5)
        self.Extra = reader.read_any(6)


    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
