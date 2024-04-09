from Jce_b import JceWriter, JceReader

from AndroidQQ.struct import PackHead_QMF
from AndroidQQ.struct.NS_MOBILE_COMM import UgcRightInfo
from AndroidQQ.struct.NS_MOBILE_OPERATION import OperationPublishmoodReq, Source, operation_publishmood_rsp
from AndroidQQ.struct.cooperation import createQmfUpstream, UnQmfDownstream


def SQQzoneSvc_publishmood(info, content: str):
    """"
    空间_说说
        :param info
        :param content 发送的内容

    # """
    busi_param = {
        32: '0',
        33: '0',
        25: '',  # 自身的名字
        41: 'quickpic_use=0'
    }

    source = Source(
        # 来源
        subtype=2,
        termtype=4,
        apptype=0
    )

    right_info = UgcRightInfo(
        # UGC 权利信息
        ugc_right=1
    )

    extend_info = {
        'is_feeds_long_pics_browsing_mode': '0'  # 是提供长图片浏览模式
    }
    stored_extend_info = {
        'is_feeds_long_pics_browsing_mode': '0',  # 是提供长图片浏览模式
        'fakeFeedAppIdForClient': '311'  # 客户端的虚假 Feed 应用程序 ID
    }
    proto_extend_info = {
        'TO_UGCSVR_FOR_FONT': bytes(b'\x0c\x1c'),
        '#CHARBUF#feedskin': bytes(b'\x08\x0c'),
    }

    PublishmoodReq = OperationPublishmoodReq(
        uin=int(info.uin),
        content=content,
        isverified=1,  # 已验证
        issynctoweibo=0,

        source=source,
        busi_param=busi_param,
        # clientkey='94ccc310-d2a2-4c32-bebf-f68435c30698',
        open_appid='',
        right_info=right_info,
        extend_info=extend_info,
        stored_extend_info=stored_extend_info,
        proto_extend_info=proto_extend_info
        #
    ).to_bytes()
    #

    OperationLikeReq = JceWriter().write_jce_struct(PublishmoodReq, 0)

    int64 = JceWriter().write_int64(int(info.uin), 0).bytes()

    Buffer = JceWriter().write_map({'publishmood': {
        'NS_MOBILE_OPERATION.operation_publishmood_req': OperationLikeReq
    }, 'hostuin': {'int64': int64}}, 0)

    Upstream = createQmfUpstream(info, 1, Buffer, 'QzoneNewService.publishmood')
    Buffer = PackHead_QMF(info, 'SQQzoneSvc.publishmood', Upstream)

    return Buffer


def SQQzoneSvc_publishmood_rsp(buffer: bytes):
    rsp_Buffer, msg, ret = UnQmfDownstream(buffer, 'publishmood', 'NS_MOBILE_OPERATION.operation_publishmood_rsp')

    if rsp_Buffer == b'':
        return {'Busi': {}, 'msg': msg, 'ret': ret}
    like_rsp = JceReader(rsp_Buffer).read_object(operation_publishmood_rsp)
    return {'Busi': like_rsp.to_dict(), 'msg': msg, 'ret': ret}


if __name__ == '__main__':
    SQQzoneSvc_publishmood('测试说说')
