from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader

from AndroidQQ.struct.SummaryCard import UserLocaleInfo


class ReqSummaryCard(IJceStruct):
    IsFriend: bool = False  # 是朋友
    ReqCommLabel: bool = False  # 是否请求通讯录标签
    ReqExtendCard: bool = False  # 是否请求扩展名片
    ReqMedalWallInfo: bool = False  # 请求勋章墙信息
    ReqNearbyGodInfo: bool = False  # 请求附近God信息
    AddFriendSource: int = 0  # 添加好友来源

    ComeFrom: int = 65535  # 来自
    GetControl: int = 0  # 获取控制
    GroupCode: int = 0  # 群号
    GroupUin: int = 0  # 群 Uin
    TinyId: int = 0  # TinyId
    Uin: int = 0  # Uin
    stLocaleInfo: UserLocaleInfo = None
    SearchName: str = ''  # 搜索名称
    LikeSource: int = 0  # 喜欢来源
    QzoneFeedTimestamp: int = 0  # Qzone Feed时间戳
    RichCardNameVer: int = 0  # 丰富的卡名

    ReqKandianInfo: bool = False  # 是否请求看点
    ReqLastGameInfo: bytes = b''  # 请求上次游戏信息
    ReqStarInfo: bytes = b''  # 请求星星信息
    ReqTemplateInfo: bytes = b''  # Req Template Info
    SecureSig: bytes = b''  # 安全的签名
    Seed: bytes = b''  # 发送?

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        jce = JceWriter()
        jce.write_int64(self.Uin, 0)
        jce.write_int64(self.ComeFrom, 1)
        jce.write_int64(self.QzoneFeedTimestamp, 2)
        jce.write_bool(self.IsFriend, 3)
        jce.write_int64(self.GroupCode, 4)
        jce.write_int64(self.GroupUin, 5)
        if self.Seed != b'':
            jce.write_bytes(self.Seed, 6)

        if self.SearchName != '':
            jce.write_string(self.SearchName, 7)

        jce.write_int64(self.GetControl, 8)
        jce.write_int64(self.AddFriendSource, 9)

        if self.SecureSig != b'':
            jce.write_bytes(self.SecureSig, 10)

        if self.ReqLastGameInfo != b'':
            jce.write_bytes(self.ReqLastGameInfo, 11)

        if self.ReqTemplateInfo != b'':
            jce.write_bytes(self.ReqTemplateInfo, 12)

        if self.ReqStarInfo != b'':
            jce.write_bytes(self.ReqStarInfo, 13)

        # 14 暂时不处理

        jce.write_int64(self.TinyId, 15)
        jce.write_int64(self.LikeSource, 16)
        if self.stLocaleInfo:
            jce.write_jce_struct(self.stLocaleInfo.to_bytes(), 17)

        jce.write_bool(self.ReqMedalWallInfo, 18)

        # 19 暂时不处理
        jce.write_bool(self.ReqNearbyGodInfo, 20)
        jce.write_bool(self.ReqCommLabel, 21)
        jce.write_bool(self.ReqExtendCard, 22)

        if self.ReqKandianInfo:
            jce.write_bool(self.ReqKandianInfo, 23)

        jce.write_int64(self.RichCardNameVer, 24)

        return jce.bytes()
