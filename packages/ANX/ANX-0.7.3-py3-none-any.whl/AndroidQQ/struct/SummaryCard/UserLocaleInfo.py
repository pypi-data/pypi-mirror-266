from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class UserLocaleInfo(IJceStruct):
    """用户区域设置信息"""
    Latitude: int = 0  # 纬度
    Longitude: int = 0  # 经度

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        jce = JceWriter()
        jce.write_int64(self.Longitude, 1)
        jce.write_int64(self.Latitude, 2)
        return jce.bytes()
