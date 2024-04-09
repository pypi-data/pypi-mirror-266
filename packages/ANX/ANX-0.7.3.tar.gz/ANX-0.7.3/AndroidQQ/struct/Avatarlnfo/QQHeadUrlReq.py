from typing import List

from Jce_b import JceWriter, JceReader
from pydantic import BaseModel, Field

from AndroidQQ import log
from AndroidQQ.struct.Avatarlnfo import DestQQHeadInfo


# struct AvatarInfo;


class QQHeadUrlReq(BaseModel):
    """QQ头像网址请求"""
    destUserInfo: List[DestQQHeadInfo] = []
    dstUsrType: int = Field(0, description="目标用户类型")
    myUin: int = 0

    def writeTo(self):
        destUserInfo_list = [info.writeTo() for info in self.destUserInfo]
        jce = JceWriter()
        jce.write_int64(self.myUin, 0)
        jce.write_jce_struct_list(destUserInfo_list, 1)
        jce.write_int32(self.dstUsrType, 2)
        return jce.bytes()


if __name__ == '__main__':
    DestInfo = DestQQHeadInfo(phoneNum="+8612131313131")
    log.info(QQHeadUrlReq(destUserInfo=[DestInfo]).writeTo().hex())
    pass
