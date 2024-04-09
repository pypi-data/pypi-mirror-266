from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader



class single_feed(IJceStruct):
    feed_attach_info: str = ""
    feed_info: str = ""
    feeds_update_time: int = 0
    feedskey: str = ""
    iUnifyRecomType: int = 0
    patch_singlefeed: dict[int, bytes] = None
    pullAll: bool = False
    recomfeeds: list[dict[int, bytes]] = None
    singlefeed: dict = None
    status: int = 0
    time: int = 0
    uContainerSubType: int = 0

    def read_from(self, reader: JceReader) -> None:
        self.singlefeed = reader.read_map(0)
        self.status = reader.read_any(1)
        self.feed_info = reader.read_string(2)
        self.feed_attach_info = reader.read_string(3)
        self.feedskey = reader.read_string(4)
        self.time = reader.read_any(5)
        self.recomfeeds = reader.read_any(6)
        self.uContainerSubType = reader.read_any(7)
        self.patch_singlefeed = reader.read_any(8)
        self.feeds_update_time = reader.read_any(9)
        self.pullAll = reader.read_any(10)
        self.iUnifyRecomType = reader.read_any(11)



    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
