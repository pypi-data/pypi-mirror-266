# package friendlist;
from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class AddFriendReq(IJceStruct):
    adduin: int = 0
    adduinsetting: int = 0
    autoSend: int = 1
    bSupportAddRelief: bool = False
    bSupportSecureTips: bool = False
    contact_bothway_friend: bool = False
    ext_info: bytes = None
    friend_src_desc: bytes = None
    macqqInfo = None
    msg: str = ""
    msgLen: int = 0
    myAllowFlag: int = 0
    myfriendgroupid: int = 0
    name: bytes = None
    name1: bytes = None
    permission_info: bytes = None
    remark: bytes = None
    secSign: bytes = None
    showMyCard: int = 0
    sig: bytes = None
    sourceID: int = 3999
    sourceSubID: int = 0
    srcFlag: int = 0
    src_description: bytes = None
    token: bytes = None
    uin: int = 0
    verify: bytes = None

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_int64(self.uin, 0)
        Jce.write_int64(self.adduin, 1)
        Jce.write_int64(self.adduinsetting, 2)
        Jce.write_int64(self.myAllowFlag, 3)  # 我的允许标志
        Jce.write_int64(self.myfriendgroupid, 4)  # 我的朋友组 ID
        Jce.write_int64(self.msgLen, 5)  # 仅消息
        Jce.write_string(self.msg, 6)
        Jce.write_int64(self.srcFlag, 7)
        Jce.write_int64(self.autoSend, 8)
        if self.sig:
            Jce.write_object(self.sig, 9)
        Jce.write_int64(self.sourceID, 10)
        Jce.write_int64(self.sourceSubID, 11)
        if self.name:
            Jce.write_object(self.name, 12)
        if self.src_description:
            Jce.write_object(self.src_description, 13)

        if self.friend_src_desc:  # 朋友 src 描述
            Jce.write_object(self.friend_src_desc, 14)

        Jce.write_object(self.contact_bothway_friend, 15)  # 联系双向朋友
        if self.remark:
            Jce.write_object(self.remark, 16)  # 备注

        if self.name1:
            Jce.write_object(self.name1, 17)  # 姓名

        Jce.write_object(self.showMyCard, 18)  # 显示我的名片

        if self.token:
            Jce.write_object(self.token, 19)

        if self.verify:
            Jce.write_object(self.verify, 20)

        if self.macqqInfo:
            Jce.write_object(self.macqqInfo, 21)  # macqq

        Jce.write_object(self.bSupportSecureTips, 22)  # 是否支持安全提示
        Jce.write_object(self.bSupportAddRelief, 23)  # b 支持添加救济
        if self.ext_info:
            Jce.write_object(self.ext_info, 24)
        if self.secSign:
            Jce.write_object(self.secSign, 25)  # 签名
        if self.permission_infoL:
            Jce.write_object(self.permission_info, 26)  # 权限信息
        return Jce.bytes()
