from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class Source(IJceStruct):
    apptype: int
    subtype: int
    termtype: int

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.subtype, 0)
        Jce.write_object(self.termtype, 1)
        Jce.write_object(self.apptype, 2)
        return Jce.bytes()
