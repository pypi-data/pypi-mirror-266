from typing import Union, List, cast

from Jce_b import IJceStruct
from Jce_b.typing import JceReader

from .single_feed import *


class mobile_applist_rsp(IJceStruct):
    album_area_info: dict = None
    album_count: int = 0

    all_applist_data: list = []
    attach_info: str = ""
    auto_load: int = 0
    dailyShuoShuoCount: int = 0
    extend_info: dict = None
    hasmore: int = 0
    kantu_album_count: int = 0
    life_moment_info: dict = None
    lossy_service: int = 0
    mapEx: dict[str, bytes] = None
    photo_count: int = 0
    remain_count: int = 0

    share_album: IJceStruct = None

    shuoshuo_timer_unpublished_count: int = 0
    stMemoryInfo: dict = None
    video_count: int = 0

    def read_from(self, reader: JceReader) -> None:
        # reader.read_head()

        self.all_applist_data = reader.read_list(single_feed, 0)

        self.hasmore = reader.read_any(1)
        self.remain_count = reader.read_any(2)
        self.attach_info = reader.read_any(3)
        self.auto_load = reader.read_any(4)

        self.share_album = reader.read_object(single_feed)
        self.lossy_service = reader.read_any(7)
        self.extend_info = reader.read_any(8)
        self.album_count = reader.read_any(9)
        self.photo_count = reader.read_any(10)
        self.video_count = reader.read_any(11)
        self.stMemoryInfo = reader.read_any_with_tag(12)
        self.mapEx = reader.read_any(13)
        self.shuoshuo_timer_unpublished_count = reader.read_any(14)
        self.life_moment_info = reader.read_any_with_tag(15)
        self.album_area_info = reader.read_any_with_tag(16)
        self.kantu_album_count = reader.read_any(17)
        self.dailyShuoShuoCount = reader.read_any(18)

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
