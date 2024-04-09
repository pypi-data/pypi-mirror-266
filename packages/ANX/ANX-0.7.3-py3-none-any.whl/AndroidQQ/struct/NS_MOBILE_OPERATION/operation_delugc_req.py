# package NS_MOBILE_OPERATION;
from typing import Any, Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class operation_delugc_req(IJceStruct):
    appid: int = 0
    busi_param: dict = None
    content: str = ''
    isverified: int = 0
    mapEx: dict = None
    ownuin: int = 0
    srcId: str = ''
    srcSubid: str = ''
    uin: int = 0

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        jce = JceWriter()
        jce.write_object(self.appid, 0)
        jce.write_object(self.uin, 1)
        jce.write_object(self.ownuin, 2)
        if self.srcId:
            jce.write_object(self.srcId, 3)

        if self.srcSubid:
            jce.write_object(self.srcSubid, 4)
        if self.content:
            jce.write_object(self.content, 5)

        jce.write_object(self.isverified, 6)
        jce.write_object(self.mapEx, 8)

        return jce.bytes()


if __name__ == '__main__':
    print(operation_delugc_req(
        appid=311,
        uin=3810573312,
        ownuin=3810573312,
        srcId='00bc20e3821cc365e3e20100'

    ).to_bytes().hex())
