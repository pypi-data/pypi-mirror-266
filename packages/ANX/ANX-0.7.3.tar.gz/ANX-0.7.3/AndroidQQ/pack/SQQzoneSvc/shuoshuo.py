import json

from Jce_b import JceWriter, JceReader

from AndroidQQ.struct import PackHead_QMF
from AndroidQQ.struct.NS_MOBILE_FEEDS import mobile_applist_req, mobile_applist_rsp
from AndroidQQ.struct.cooperation import createQmfUpstream, UnQmfDownstream
from AndroidQQ.struct.feedcomponent.model import JceCellData
from AndroidQQ.utils import to_serializable


def SQQzoneSvc_shuoshuo(info, Uin: int):
    """
        获取说说列表
            :param info
            :param Uin 目标账号
            :return:

    """
    mapEx = {
        'mobile_detail_info': 'V1916A&9&28&4&2'
    }
    int64 = JceWriter().write_int64(int(info.uin), 0).bytes()

    applist_req = mobile_applist_req(
        uin=Uin,
        appid=311,
        count=10,
        attach_info='',
        album_show_type=0,
        refresh_type=1,
        extrance_type=0,
        mapEx=mapEx,
    ).to_bytes()
    Buffer = JceWriter().write_jce_struct(applist_req, 0)
    Buffer = JceWriter().write_map({'shuoshuo': {
        'NS_MOBILE_FEEDS.mobile_applist_req': Buffer
    }, 'hostuin': {'int64': int64}}, 0)

    Upstream = createQmfUpstream(info, 1, Buffer, 'QzoneNewService.applist.shuoshuo')
    Buffer = PackHead_QMF(info, 'SQQzoneSvc.shuoshuo', Upstream)

    return Buffer


def SQQzoneSvc_shuoshuo_rsp(Buffer: bytes, fullText: bool):
    def _human_reading():
        """
            人类可阅读
        """
        rsp = {}
        shuoshuo_list = []
        for item in applist_rsp.all_applist_data:
            CellDat = JceCellData(item.singlefeed)

            shuoshuo_list.append({'busi_param': CellDat.cell_operation.busi_param})

        rsp.update({'shuoshuo_list': shuoshuo_list})
        return rsp

    rsp_Buffer, msg, ret = UnQmfDownstream(Buffer, 'shuoshuo', 'NS_MOBILE_FEEDS.mobile_applist_rsp')

    if rsp_Buffer == b'':
        return {'Busi': {}, 'msg': msg, 'ret': ret}
    applist_rsp = JceReader(rsp_Buffer).read_object(mobile_applist_rsp)

    if fullText:
        # 全文返回
        return {'Busi': to_serializable(applist_rsp), 'msg': msg, 'ret': ret}
    else:
        return {'Busi': _human_reading(), 'msg': msg, 'ret': ret}
