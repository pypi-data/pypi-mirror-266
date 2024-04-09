# struct AvatarInfo;
from typing import List, Union, cast

from Jce_b import JceReader, IJceStruct

from AndroidQQ.struct.Avatarlnfo.QQHeadInfo import QQHeadInfo


class QQHeadUrlResp(IJceStruct):
    UserHeadInfoList: List[QQHeadInfo] = []  # 使用 List 替代 Java 的 ArrayList
    myUin: int = 0
    result: int = 0

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass

    def read_from(self, reader: JceReader) -> None:
        self.myUin = reader.read_int64(0)
        self.result = reader.read_int32(1)
        self.UserHeadInfoList = cast(List[QQHeadInfo], reader.read_list(QQHeadInfo, 2))

    def to_dict(self) -> dict:
        return self.__dict__
