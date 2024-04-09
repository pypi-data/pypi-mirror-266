from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader
from .s_arkshare import s_arkshare


class s_outshare(IJceStruct):
    action_url: str = ""
    ark_sharedata: IJceStruct = None
    photourl: dict = None  # 懒的折腾
    summary: str = ""
    title: str = ""

    def read_from(self, reader: JceReader) -> None:
        self.title = reader.read_any(0)
        self.summary = reader.read_any(1)
        self.photourl = reader.read_any_with_tag(2)
        self.ark_sharedata = reader.read_object(s_arkshare)
        self.action_url = reader.read_any(4)
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
