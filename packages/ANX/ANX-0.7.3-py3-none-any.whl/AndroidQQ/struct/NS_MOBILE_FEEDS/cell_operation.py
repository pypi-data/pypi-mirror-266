from typing import Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader

from AndroidQQ.struct.NS_MOBILE_FEEDS.s_outshare import s_outshare


class cell_operation(IJceStruct):
    busi_param: dict = None
    button_gif_url: str = ""
    bypass_param: dict = None
    click_stream_report: dict = None
    custom_btn: list = None
    droplist_cookie: dict = None
    feed_report_cookie: dict = None
    generic_url: str = ""
    offline_resource_bid: int = 0
    qboss_trace: str = ""
    qq_url: str = ""
    rank_param: dict = None
    recomm_cookie: dict = None
    schema_info: dict = None
    share_info: IJceStruct = None
    weixin_url: str = ""

    def read_from(self, reader: JceReader) -> None:
        self.busi_param = reader.read_any(0)
        self.weixin_url = reader.read_any(1)
        self.qq_url = reader.read_any(2)
        self.share_info = reader.read_object(s_outshare)
        self.schema_info = reader.read_any(4)
        self.recomm_cookie = reader.read_any(5)
        self.click_stream_report = reader.read_any(6)
        self.qboss_trace = reader.read_any(7)
        self.custom_btn = reader.read_any(8)
        self.feed_report_cookie = reader.read_map(9)
        self.generic_url = reader.read_any(10)
        self.bypass_param = reader.read_any(11)
        self.droplist_cookie = reader.read_any(12)
        self.rank_param = reader.read_any(13)
        self.button_gif_url = reader.read_any(14)
        self.offline_resource_bid = reader.read_any(15)

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
