from typing import Union

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class mobile_applist_req(IJceStruct):
    album_show_type: int = 0
    appid: int = 0
    attach_info: str = ""
    count: int = 10
    extrance_type: int = 0
    mapEx: dict = None
    refresh_type: int = 0
    uin: int = 0

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        Jce = JceWriter()
        Jce.write_object(self.uin, 0)
        Jce.write_object(self.appid, 1)
        Jce.write_object(self.count, 2)
        if self.attach_info is not None:
            Jce.write_object(self.attach_info, 3)

        Jce.write_object(self.album_show_type, 4)
        Jce.write_object(self.refresh_type, 5)

        Jce.write_object(self.extrance_type, 6)
        Jce.write_object(self.mapEx, 7)
        return Jce.bytes()
