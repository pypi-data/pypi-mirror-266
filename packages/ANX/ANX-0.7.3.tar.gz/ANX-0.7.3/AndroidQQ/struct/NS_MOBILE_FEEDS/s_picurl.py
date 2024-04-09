from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class s_picurl(IJceStruct):
    enlarge_rate: int = 200
    focus_x: int = 0
    focus_y: int = 0
    height: int = 0
    md5: str = ""
    size: int = 0
    url: str = ""
    width: int = 0

    def read_from(self, reader: JceReader) -> None:
        self.url = reader.read_any(0)
        self.width = reader.read_any(1)
        self.height = reader.read_any(2)
        self.focus_x = reader.read_any(3)
        self.focus_y = reader.read_any(4)
        self.enlarge_rate = reader.read_any(5)
        self.size = reader.read_any(6)
        self.md5 = reader.read_any(7)

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
