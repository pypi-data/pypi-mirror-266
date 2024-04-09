# package QMF_PROTOCAL;
from .QmfClientIpInfo import *

from .QmfTokenInfo import *
from .RetryInfo import *


class QmfUpstream(IJceStruct):
    Appid: int
    BusiBuff: bytes
    DeviceInfo: str
    Extra: bytes
    IpInfo: QmfClientIpInfo
    Qua: str
    Seq: int
    ServiceCmd: str
    Token: QmfTokenInfo
    Uin: int
    flag: int
    retryinfo: RetryInfo
    sessionID: int

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.Seq, 0)
        Jce.write_object(self.Appid, 1)
        Jce.write_object(self.Uin, 2)
        Jce.write_object(self.Qua, 3)
        Jce.write_object(self.ServiceCmd, 4)
        Jce.write_object(self.DeviceInfo, 5)
        Jce.write_jce_struct(self.Token.to_bytes(), 6)
        Jce.write_jce_struct(self.IpInfo.to_bytes(), 7)
        Jce.write_object(self.BusiBuff, 8)
        Jce.write_object(self.Extra, 9)
        Jce.write_object(self.flag, 10)
        Jce.write_object(self.sessionID, 11)
        if self.retryinfo is not None:
            Jce.write_jce_struct(self.retryinfo.to_bytes(), 12)
        return Jce.bytes()
