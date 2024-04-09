# package QMF_PROTOCAL;
from typing import Union

from Jce_b import IJceStruct, JceReader, JceWriter


class RetryInfo(IJceStruct):
    Flag: int = 0
    PkgId: int = 0
    RetryCount: int = 0

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.Flag, 0)
        Jce.write_object(self.RetryCount, 1)
        Jce.write_object(self.PkgId, 2)

        return Jce.bytes()
