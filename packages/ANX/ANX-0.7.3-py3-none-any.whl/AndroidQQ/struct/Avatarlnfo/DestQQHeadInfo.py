from Jce_b import JceWriter
from pydantic import BaseModel


class DestQQHeadInfo(BaseModel):
    dstUin: int = 0
    dwTimestamp: int = 0
    phoneNum: str = None

    def writeTo(self):
        """目标用户信息"""
        jce = JceWriter()
        jce.write_int64(self.dstUin, 0)
        jce.write_int64(self.dwTimestamp, 1)
        if self.phoneNum is not None:
            jce.write_string(self.phoneNum, 2)
        return jce.bytes()
