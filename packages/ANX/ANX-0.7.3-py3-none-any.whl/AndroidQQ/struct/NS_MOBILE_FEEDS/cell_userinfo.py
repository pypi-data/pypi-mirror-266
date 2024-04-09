from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class cell_userinfo(IJceStruct):
    # 用户信息
    action_desc: str = ""
    actiontype: int = 5
    luckyMoneyPics: list[str] = []
    user:dict = None  # 不解析

    def read_from(self, reader: JceReader) -> None:
        self.user = reader.read_any(0)
        self.action_desc = reader.read_string(1)
        self.actiontype = reader.read_int32(2)
        self.luckyMoneyPics = reader.read_any(3)

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
