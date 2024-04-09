# package NS_MOBILE_FEEDS;

from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class cell_comm(IJceStruct):
    # 通讯
    actiontype: int = 0
    actionurl: str = ""
    adv_stytle: int = 0
    adv_subtype: int = 0
    appid: int = 0
    clientkey: str = ""
    curlikekey: str = ""
    # custom_droplist: Optional[List[S_droplist_option]] = None
    editmask: int = 4294967295
    # extendInfo: Optional[Dict[str, str]] = None
    # extendInfoData: Optional[Dict[str, bytes]] = None
    feedsDelTime: int = 0
    feedsattr: int = 0
    feedsattr2: int = 0
    feedsattr3: int = 0
    feedsid: str = ""
    feedskey: str = ""
    feedstype: int = 0
    hot_score: int = 0
    iClick_area: int = 0
    interestkey: str = ""
    is_kuolie: bool = False
    is_stay: bool = False
    operatemask: int = 0
    operatemask2: int = 0
    operatemask3: int = 0
    orglikekey: str = ""
    originaltype: int = 0
    paykey: str = ""
    positionmask: int = 0
    positionmask2: int = 0
    pull_qzone: bool = False
    recom_show_type: int = 0
    recomlayout: int = 0
    recomreportid: int = 0
    recomtype: int = 0
    refer: str = ""
    reportfeedsattr: int = 0
    right_info: dict = None  # UgcRightInfo 不解析
    shield: int = 0
    show_mask: int = 0
    space_right: int = 0
    sqDynamicFeedsKey: str = ""
    # stMapABTest: Optional[Dict[int, int]] = None
    subid: int = 0
    time: int = 0
    uflag: int = 0
    ugckey: str = ""
    ugcrightkey: str = ""
    wup_feeds_type: int = 0

    def read_from(self, reader: JceReader) -> None:
        self.appid = reader.read_any(0)
        self.subid = reader.read_any(1)
        self.refer = reader.read_any(2)
        self.time = reader.read_any(3)
        self.actiontype = reader.read_any(4)
        self.actionurl = reader.read_any(5)
        self.originaltype = reader.read_any(6)
        self.operatemask = reader.read_any(7)
        self.feedskey = reader.read_any(8)
        self.orglikekey = reader.read_any(9)
        self.curlikekey = reader.read_any(10)
        self.feedstype = reader.read_any(11)
        self.feedsattr = reader.read_any(12)
        self.ugckey = reader.read_any(13)
        self.clientkey = reader.read_any(14)
        self.show_mask = reader.read_any(15)
        self.uflag = reader.read_any(16)
        self.shield = reader.read_any(17)
        self.ugcrightkey = reader.read_any(18)
        self.interestkey = reader.read_any(19)
        self.recomtype = reader.read_any(20)
        self.feedsid = reader.read_any(21)
        self.adv_stytle = reader.read_any(22)
        self.adv_subtype = reader.read_any(23)
        self.right_info = reader.read_any_with_tag(24)
        self.recomlayout = reader.read_any(25)
        self.recomreportid = reader.read_any(26)
        self.space_right = reader.read_any(27)
        self.reportfeedsattr = reader.read_any(28)
        self.recom_show_type = reader.read_any(29)
        self.wup_feeds_type = reader.read_any(30)

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
