# package QMF_PROTOCAL;
from typing import Union

from Jce_b import IJceStruct, JceReader, JceWriter


class QmfTokenInfo(IJceStruct):
    Key: bytes = b''
    Type: int = 0
    ext_key: dict = {}

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.Type, 0)
        Jce.write_object(self.Key, 1)
        if self.ext_key is not None:
            Jce.write_map(self.ext_key, 2)

        return Jce.bytes()
