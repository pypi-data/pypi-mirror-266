# package QMF_PROTOCAL;
from typing import Union

from Jce_b import IJceStruct, JceReader, JceWriter


class QmfClientIpInfo(IJceStruct):
    ClientIpv4: int = 0
    ClientIpv6: bytes = bytes()
    ClientPort: int = 0
    IpType: int = 0

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.IpType, 0)
        Jce.write_object(self.ClientPort, 1)
        Jce.write_object(self.ClientIpv4, 2)
        if self.ClientIpv6 is not None:
            Jce.write_object(self.ClientIpv6, 3)

        return Jce.bytes()
