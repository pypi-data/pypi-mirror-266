from Jce_b import JceWriter

from AndroidQQ.struct import PackHead_QMF
from AndroidQQ.struct.NS_MOBILE_OPERATION import operation_delugc_req
from AndroidQQ.struct.cooperation import createQmfUpstream, UnQmfDownstream


def SQQzoneSvc_delUgc(info, srcId):
    """
        删除说说
    """
    mapEx = {
        'del_all_media_file': '0'
    }

    int64 = JceWriter().write_int64(int(info.uin), 0).bytes()
    delugc_req = operation_delugc_req(
        appid=311,
        uin=int(info.uin),
        ownuin=int(info.uin),
        srcId=srcId,
        mapEx=mapEx,
    ).to_bytes()
    Buffer = JceWriter().write_jce_struct(delugc_req, 0)

    Buffer = JceWriter().write_map({'delUgc': {
        'NS_MOBILE_OPERATION.operation_delugc_req': Buffer
    }, 'hostuin': {'int64': int64}}, 0)

    Upstream = createQmfUpstream(info, 1, Buffer, 'QzoneNewService.delUgc')
    Buffer = PackHead_QMF(info, 'SQQzoneSvc.delUgc', Upstream)
    return Buffer


def SQQzoneSvc_delUgc_rsp(buffer):
    rsp_Buffer, msg, ret = UnQmfDownstream(buffer, 'delUgc', 'NS_MOBILE_OPERATION.operation_delugc_rsp')
    return {'msg': msg, 'ret': ret}
