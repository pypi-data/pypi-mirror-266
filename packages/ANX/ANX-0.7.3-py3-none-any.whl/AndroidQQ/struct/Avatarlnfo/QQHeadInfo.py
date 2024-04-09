from typing import Union

from Jce_b import JceReader, IJceStruct


class QQHeadInfo(IJceStruct):
    apngFaceFlag: int = 0  # 使用 int 替代 Java 的 byte
    cHeadType: int = 0
    downLoadUrl: str = ""
    dstUsrType: int = 0
    dwFaceFlgas: int = 0
    dwTimestamp: int = 0  # 使用 int 替代 Java 的 long
    headLevel: int = 0
    headVerify: str = ""
    idType: int = 0
    originUsrType: int = 0
    phoneNum: str = ""
    sizeType: int = 0
    systemHeadID: int = 0  # 使用 int 替代 Java 的 short
    uin: int = 0

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass

    def read_from(self, reader: JceReader) -> None:
        self.uin = reader.read_int64(0)
        self.dwTimestamp = reader.read_int64(1)
        self.cHeadType = reader.read_int32(2)
        self.dstUsrType = reader.read_int32(3)
        self.dwFaceFlgas = reader.read_int64(4)
        self.downLoadUrl = reader.read_string(5)
        self.systemHeadID = reader.read_int64(6)
        self.phoneNum = reader.read_string(7)
#       实践还返回了一个8
