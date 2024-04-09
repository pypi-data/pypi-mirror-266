from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class QmfBusiControl(IJceStruct):
    compFlag: int
    lenBeforeComp: int
    rspCompFlag: int

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.compFlag, 0)
        Jce.write_object(self.lenBeforeComp, 1)
        Jce.write_object(self.compFlag, 2)
        return Jce.bytes()
