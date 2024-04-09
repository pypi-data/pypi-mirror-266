from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class s_arkshare(IJceStruct):
    ark_content: str = ""
    ark_id: str = ""
    view_id: str = ""

    def read_from(self, reader: JceReader) -> None:
        self.ark_id = reader.read_any(0)
        self.view_id = reader.read_any(1)
        self.ark_content = reader.read_any(2)
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
