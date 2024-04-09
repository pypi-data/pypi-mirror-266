# struct com.tencent.msf.service.protocol.push;
from typing import Union, List

from Jce_b import IJceStruct, JceWriter
from Jce_b.typing import JceReader


class SvcReqRegister(IJceStruct):
    # 类型注解
    bIsOnline: bool = False  # 是否在线
    bIsSetStatus: bool = False  # 是否设置状态
    bIsShowOnline: bool = False  # 是否显示在线
    bKikPC: bool = False  # 是否强网
    bKikWeak: bool = False  # 是否弱网
    bOnlinePush: bool = True  # 是否在线推送
    bOpenPush: bool = True
    bRegType: bool = False
    bSetMute: bool = False  # 设置沉默
    bSlientPush: bool = False
    bTimActiveFlag: bool = True
    # bytes_0x769_reqbody: Optional[bytes] = None
    cBindUinNotifySwitch: int = 1
    cConnType: int = 0
    cNetType: int = 0
    cNotifySwitch: int = 1
    iBatteryStatus: int = 0
    iLargeSeq: int = 0
    iLastWatchStartTime: int = 0
    iLocaleID: int = 2052
    iOSVersion: int = 0
    iStatus: int = 11  # 我的状态
    lBid: int = 0
    lCpId: int = 0
    lUin: int = 0
    lVendorDevId: int = 0
    sBuildVer: str = ""
    sChannelNo: str = ""
    sOther: str = ""
    # stVendorPushInfo: Optional['VendorPushInfo'] = None  # Assuming 'VendorPushInfo' is a class defined elsewhere
    strDevName: str = ""
    strDevType: str = ""
    strIOSIdfa: str = ""
    strOSVer: str = ""
    strVendorName: str = ""
    strVendorOSName: str = ""
    timeStamp: int = 0
    uExtOnlineStatus: int = 0
    uNewSSOIp: int = 0
    uOldSSOIp: int = 0

    vecBindUin: List[int] = None
    vecCustomStatus: bytes = None
    vecDevParam: bytes = None
    vecGuid: bytes = None
    vecServerBuf: bytes = None

    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        jce = JceWriter()
        jce.write_object(self.lUin, 0)
        jce.write_object(self.lBid, 1)
        jce.write_object(self.cConnType, 2)
        jce.write_object(self.sOther, 3)
        jce.write_object(self.iStatus, 4)
        jce.write_object(self.bOnlinePush, 5)
        jce.write_object(self.bIsOnline, 6)
        jce.write_object(self.bIsSetStatus, 7)
        jce.write_object(self.bKikPC, 8)
        jce.write_object(self.bKikWeak, 9)
        jce.write_object(self.timeStamp, 10)
        jce.write_object(self.iOSVersion, 11)
        jce.write_object(self.cNetType, 12)

        if self.sBuildVer is not None:
            jce.write_object(self.sBuildVer, 13)

        jce.write_object(self.bRegType, 14)

        if self.vecDevParam is not None:
            jce.write_object(self.vecDevParam, 15)

        if self.vecGuid is not None:
            jce.write_object(self.vecGuid, 16)

        jce.write_object(self.iLocaleID, 17)
        jce.write_object(self.bSlientPush, 18)

        if self.strDevName != '':
            jce.write_object(self.strDevName, 19)

        if self.strDevType != '':
            jce.write_object(self.strDevType, 20)

        if self.strOSVer != '':
            jce.write_object(self.strOSVer, 21)

        jce.write_object(self.bOnlinePush, 22)
        jce.write_object(self.iLargeSeq, 23)
        jce.write_object(self.iLastWatchStartTime, 24)

        if self.vecBindUin is not None:
            jce.write_object(self.vecBindUin, 25)

        jce.write_object(self.uOldSSOIp, 26)

        jce.write_object(self.uNewSSOIp, 27)

        if self.sChannelNo != '':
            jce.write_object(self.sChannelNo, 28)

        jce.write_object(self.lCpId, 29)
        # 后面懒地传了

        return jce.bytes()
