from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class cmshow_active_result(IJceStruct):
    cm_cardli_count: int = 0
    cm_stone_count: int = 0
    fire_score: int = 0
    is_reach_friend_limit: int = 0
    is_reach_limit: int = 0

    def read_from(self, reader: JceReader) -> None:
        self.fire_score = reader.read_any(1)
        self.cm_stone_count = reader.read_any(2)
        self.is_reach_limit = reader.read_any(3)
        self.cm_cardli_count = reader.read_any(4)
        self.is_reach_friend_limit = reader.read_any(5)
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
