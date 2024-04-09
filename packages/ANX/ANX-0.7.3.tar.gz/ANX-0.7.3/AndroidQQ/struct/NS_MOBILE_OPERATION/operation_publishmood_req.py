from typing import Union

from Jce_b import IJceStruct, JceWriter, JceReader
from .Source import Source
from ..NS_MOBILE_COMM import UgcRightInfo


class OperationPublishmoodReq(IJceStruct):
    busi_param: dict = None
    clientkey: str = ""
    content: str = ""
    extend_info: dict = None
    frames: int = 0
    hidden_poi: IJceStruct = None
    isWinPhone: int = 0
    issynctoweibo: bool = True
    isverified: bool = True
    lbsinfo: IJceStruct = None
    lock_days: int = 0
    mediaSubType: int = 0
    mediabittype: int = 0
    mediainfo: IJceStruct = None
    mediatype: int = 0
    modifyflag: int = 0
    open_appid: str = ""
    proto_extend_info: dict = None
    publishTime: int = 0
    richtype: str = ""
    richval: str = ""
    right_info: UgcRightInfo = None
    seal_id: int = 0
    shootInfo: IJceStruct = None
    source: Source = None
    sourceName: str = ""
    srcid: str = ""
    stored_extend_info: dict = None
    uin: int = 0
    weibourl: str = ""

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.uin, 0)
        if self.content:
            Jce.write_string(self.content, 1)

        Jce.write_object(self.isverified, 2)
        Jce.write_object(self.issynctoweibo, 3)
        if self.weibourl:
            Jce.write_object(self.weibourl, 4)
        Jce.write_object(self.mediatype, 5)
        #
        Jce.write_jce_struct(b'', 6)  # mediaInfo 暂时不处理

        if self.lbsinfo:
            Jce.write_object(self.lbsinfo, 7)

        # print(self.source)
        if self.source:
            Jce.write_jce_struct(self.source.to_bytes(), 8)
        Jce.write_object(self.mediabittype, 9)
        if self.busi_param:
            Jce.write_map(self.busi_param, 10)

        if self.clientkey:
            Jce.write_string(self.clientkey, 11)
        #

        Jce.write_string(self.open_appid, 12)
        #
        if self.right_info:
            Jce.write_jce_struct(self.right_info.to_bytes(), 13)
        Jce.write_jce_struct(bytes.fromhex('0a 3c 56 00 6c 76 00 8c 9c ac 0b 1c '), 14)  # 拍摄信息

        Jce.write_object(self.publishTime, 15)
        Jce.write_object(self.mediaSubType, 16)
        Jce.write_string(self.srcid, 17)

        Jce.write_object(self.modifyflag, 18)
        if self.extend_info:
            Jce.write_map(self.extend_info, 19)
        Jce.write_object(self.richtype, 20)
        Jce.write_object(self.richval, 21)
        Jce.write_object(self.isWinPhone, 22)
        Jce.write_object(self.sourceName, 23)
        if self.hidden_poi:
            Jce.write_object(self.hidden_poi, 24)
        Jce.write_object(self.seal_id, 25)
        Jce.write_object(self.frames, 26)
        Jce.write_object(self.lock_days, 27)
        if self.stored_extend_info:
            Jce.write_object(self.stored_extend_info, 28)
        if self.proto_extend_info:
            Jce.write_map(self.proto_extend_info, 29)
        return Jce.bytes()
