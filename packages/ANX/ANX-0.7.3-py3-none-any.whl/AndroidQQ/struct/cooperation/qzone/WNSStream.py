# package cooperation.qzone;
import time
import zlib
from typing import Union

from Jce_b import JceWriter, JceReader, IJceStruct

from AndroidQQ.struct.QMF_PROTOCAL import QmfUpstream, QmfTokenInfo, QmfClientIpInfo, QmfBusiControl, RetryInfo, \
    QmfDownstream


def createBusiControl(compFlag, length, SUPPORT_COMPRESS):
    Qmf_Busi_Control = QmfBusiControl(
        compFlag=compFlag,
        lenBeforeComp=length,  # 补偿前的长度
        rspCompFlag=SUPPORT_COMPRESS
    ).to_bytes()
    _Buffer = JceWriter().write_jce_struct(Qmf_Busi_Control, 0)

    _Buffer = JceWriter().write_map({'busiCompCtl': {
        'QMF_PROTOCAL.QmfBusiControl': _Buffer
    }}, 0)
    return _Buffer


def createQmfUpstream(info, compFlag: int, BusiBuff: bytes, ServiceCmd: str):
    """"
            创建 Qmf
                compFlag: 比较标志  1 =压缩
                BusiBuff: 业务数据
    """

    Extra = createBusiControl(
        compFlag=compFlag,
        length=len(BusiBuff),  # 压缩前的长度
        SUPPORT_COMPRESS=1

    )

    TokenInfo = QmfTokenInfo(
        Type=64,
        Key=b'',
        ext_key={1: bytearray.fromhex('00')}
    )

    ClientIpInfo = QmfClientIpInfo(
        IpType=0,
        ClientPort=0,
        ClientIpv4=0,
        ClientIpv6=bytearray.fromhex('00 00 00 00 00 00')
    )

    _RetryInfo = RetryInfo(
        Flag=1,
        RetryCount=0,
        PkgId=int(time.time() * 1000)

    )
    if compFlag:
        BusiBuff = zlib.compress(BusiBuff)
    Upstream = QmfUpstream(
        Seq=info.seq,
        Appid=1000027,
        Uin=int(info.uin),
        Qua='V1_AND_SQ_8.9.83_4680_YYB_D',
        ServiceCmd=ServiceCmd,
        # DeviceInfo='i=8e47e13209285931450588fb100013d16b0b&imsi=8e47e13209285931450588fb100013d16b0b&mac=02:00:00:00:00:00&m=V1916A&o=9&a=28&sd=0&c64=1&sc=1&p=540*960&aid=8e47e13209285931450588fb100013d16b0b&f=vivo&mm=3946&cf=2798&cc=4&qimei=8e47e13209285931450588fb100013d16b0b&qimei36=8e47e13209285931450588fb100013d16b0b&sharpP=1&n=wifi&support_xsj_live=true&client_mod=default&qadid=&md5_android_id=&md5_mac=&client_ipv4=&aid_ticket=&taid_ticket=0101869FEA6C27834C685B0CF0ED44C4516C368A5F048AE3AA301973FA34D55425FBFF12CA010BAB2CE55BFB&muid=&muid_type=0&device_ext=%7B%22attri_info%22%3A%7B%22ua%22%3A%22Dalvik%5C%2F2.1.0+%28Linux%3B+U%3B+Android+9%3B+V1916A+Build%5C%2FPQ3B.190801.002%29%22%2C%22ua_i%22%3A%7B%22c_i%22%3A%2291.0.4472.114%22%2C%22s_i%22%3A%7B%22b_i%22%3A%22PQ3B.190801.002%22%2C%22b_m%22%3A%22V1916A%22%2C%22b_mf%22%3A%22vivo%22%2C%22b_r_o_c%22%3A%229%22%2C%22b_v_c%22%3A%22REL%22%2C%22b_v_i%22%3A%22G9650ZHU2ARC6%22%2C%22b_v_r%22%3A%229%22%2C%22jvm_v%22%3A%222.1.0%22%2C%22sw_s%22%3A%221%22%7D%7D%7D%2C%22font_size%22%3A1%2C%22harmony_sys_info%22%3A%7B%22harmony_pure_mode%22%3A-1%2C%22is_harmony_os%22%3Afalse%7D%2C%22hevc_compatibility_info%22%3A%5B%7B%22max_fps%22%3A30%2C%22max_luma_samples%22%3A%22921600%22%2C%22video_player_type%22%3A1%7D%5D%2C%22jump_ability%22%3A%5B9999%5D%2C%22module_name%22%3A%22pcad-reward%22%2C%22mqq_config_status%22%3A1%2C%22qi36%22%3A%228e47e13209285931450588fb100013d16b0b%22%2C%22qqb_external_exp_info%22%3A%7B%22exp_id%22%3A%5B%22gdt_tangram_qq_android_000006%22%2C%22gdt_tangram_qq_android_000010%22%5D%2C%22traffic_type%22%3A26%7D%2C%22targeting_ability%22%3A%7B%22support_quick_app_link%22%3Afalse%2C%22web_wx_mgame%22%3Atrue%7D%2C%22wechat_installed_info%22%3A%7B%22api_ver%22%3A%220%22%7D%7D&video_auto_play=1&sound_auto_play=0&qimei=8e47e13209285931450588fb100013d16b0b&longitude=&latitude=&coordtype=0&timezone=+8,id:Asia/Shanghai&is_teenager_mod=0&is_care_mod=0&feeds_new_style=1&feed_in_tab=0&AV1=1&hwlevel=1',
        DeviceInfo='',
        Token=TokenInfo,
        IpInfo=ClientIpInfo,
        BusiBuff=BusiBuff,
        Extra=Extra,
        flag=0,
        sessionID=0,
        retryinfo=_RetryInfo,

    ).to_bytes()

    return Upstream


def UnQmfDownstream(Buffer: bytes, key_1: str, key_2: str):
    """解QMF"""

    stream = QmfDownstream()
    stream.read_from(JceReader(Buffer))

    Buffer_head = stream.BusiBuff[:1]
    if Buffer_head == bytearray(b'x'):
        BusiBuff = zlib.decompress(stream.BusiBuff)
    else:
        BusiBuff = stream.BusiBuff

    BusiBuff = JceReader(BusiBuff).read_map(0)

    rsp_Buffer = BusiBuff.get(key_1, {}).get(key_2, b'')
    msg_Buffer = BusiBuff.get('msg', {}).get('string', b'')
    ret_Buffer = BusiBuff.get('ret', {}).get('int32', b'')
    msg = JceReader(msg_Buffer).read_string(0)
    ret = JceReader(ret_Buffer).read_int64(0)

    return rsp_Buffer, msg, ret
