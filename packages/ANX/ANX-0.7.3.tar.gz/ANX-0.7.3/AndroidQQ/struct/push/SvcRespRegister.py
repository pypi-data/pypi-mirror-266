# struct com.tencent.msf.service.protocol.push;
from typing import Optional, Union

from Jce_b import IJceStruct
from Jce_b.typing import JceReader


class SvcRespRegister(IJceStruct):
    # 类变量的静态缓存
    # cache_bytes_0x769_rspbody = bytes([0])
    # cache_vecCustomStatus = bytes([0])
    bCrashFlag: bool = False
    bLargeSeqUpdate: bool = False
    bLogQQ: bool = False
    bNeedKik: bool = False
    bUpdateFlag: bool = False
    bytes_0x769_rspbody: Optional[bytes] = None
    cReplyCode: int = 0
    iClientPort: int = 0
    iHelloInterval: int = 300
    iLargeSeq: int = 0
    iStatus: int = 0
    lBid: int = 0
    lServerTime: int = 0
    lUin: int = 0
    strClientIP: str = ""
    strResult: str = ""
    timeStamp: int = 0
    uClientAutoStatusInterval: int = 600
    uClientBatteryGetInterval: int = 86400
    uExtOnlineStatus: int = 0
    vecCustomStatus: Optional[bytes] = None

    def read_from(self, reader: JceReader) -> None:
        self.lUin = reader.read_any(0)
        self.lBid = reader.read_any(1)
        self.cReplyCode = reader.read_any(2)
        self.strResult = reader.read_any(3)
        self.lServerTime = reader.read_any(4)
        self.bLogQQ = reader.read_any(5)
        self.bNeedKik = reader.read_any(6)
        self.bUpdateFlag = reader.read_any(7)
        self.timeStamp = reader.read_any(8)
        self.bCrashFlag = reader.read_any(9)
        self.strClientIP = reader.read_any(10)
        self.iClientPort = reader.read_any(11)
        self.iHelloInterval = reader.read_any(12)
        self.iLargeSeq = reader.read_any(13)
        self.bLargeSeqUpdate = reader.read_any(14)
        self.bytes_0x769_rspbody = reader.read_any(15)
        self.iStatus = reader.read_any(16)
        self.uExtOnlineStatus = reader.read_any(17)
        self.uClientBatteryGetInterval = reader.read_any(18)
        self.uClientAutoStatusInterval = reader.read_any(19)
        self.vecCustomStatus = reader.read_any(21)

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass

    def to_dict(self) -> dict:
        return self.__dict__
