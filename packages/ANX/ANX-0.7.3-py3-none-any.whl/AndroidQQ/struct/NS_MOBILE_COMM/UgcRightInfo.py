from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class UgcRightInfo(IJceStruct):
    ugc_right: int = 0

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.ugc_right, 0)
        return Jce.bytes()
