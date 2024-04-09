# struct QQService;
from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader

from AndroidQQ import log


class SvcReqGetDevLoginInfo(IJceStruct):
    iGetDevListType: int = 7
    iLoginType: int = 1
    iNextItemIndex: int = 0
    iRequireMax: int = 0
    iTimeStamp: int = 0
    strAppName: str = ""  # com.tencent.mobileqq
    vecGuid: bytes = b''

    def to_bytes(self) -> Union[bytes, bytearray]:
        jce = JceWriter()
        jce.write_bytes(self.vecGuid, 0)
        jce.write_string(self.strAppName, 1)
        jce.write_int64(self.iTimeStamp, 2)
        jce.write_int64(self.iTimeStamp, 3)
        jce.write_int64(self.iNextItemIndex, 4)
        jce.write_int64(self.iRequireMax, 5)
        jce.write_int64(self.iGetDevListType, 6)
        return jce.bytes()

    def read_from(self, reader: JceReader) -> None:
        pass


if __name__ == '__main__':
    buffer = SvcReqGetDevLoginInfo(
        # vecGuid=self.info.Guid,
        iTimeStam=1,
        strAppName='com.tencent.mobileqq',
        iRequireMax=20
    ).to_bytes()
    log.info(buffer.hex())
