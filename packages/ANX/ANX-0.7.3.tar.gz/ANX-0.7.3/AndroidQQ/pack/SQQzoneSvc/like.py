from Jce_b import JceWriter, JceReader

from AndroidQQ.struct.cooperation import createQmfUpstream, UnQmfDownstream
from AndroidQQ.struct import PackHead_QMF
from AndroidQQ.struct.NS_MOBILE_OPERATION import operation_like_req, operation_like_rsp


def SQQzoneSvc_like(info, target_Uin: int, title: str, feedskey: str):
    def _operation_like_req():
        int64 = JceWriter().write_int64(int(info.uin), 0).bytes()
        curkey = f'http://user.qzone.qq.com/{target_Uin}/mood/{feedskey}'

        busi_param = {
            # 最终生成的会和腾讯有所不同,但似乎没有影响
            97: f'&feedtype1=1&feedtype2=3&feedtype3=1&org_uniq_key=&sUniqId={target_Uin}_311_{feedskey}&fExposUniqId=&colorexptid=0&colorstrategyid=0',
            156: f'appid:311 typeid:0 feedtype:2 hostuin:{info.uin} feedskey:{feedskey} ',
            4: '',
            5: curkey,
            101: f'0=&1=&2=&3=&4={target_Uin}&5=&6=0&7=&8=&9=&10=0&76=',
            6: curkey,
            104: '',
            141: '',
            142: '5',
            207: '0',
            48: '0',
            52: '',
            23: '0',
            184: title,
            121: f'&feedtype1=1&feedtype2=3&feedtype3=1&org_uniq_key=&sUniqId={target_Uin}_311_{feedskey}&fExposUniqId=&colorexptid=0&colorstrategyid=0'}

        OperationLikeReq = operation_like_req(uin=int(info.uin),
                                              curkey=curkey,
                                              unikey=curkey,
                                              action=0,
                                              appid=311,
                                              busi_param=busi_param,
                                              hostuin=0
                                              ).to_bytes()

        OperationLikeReq = JceWriter().write_jce_struct(OperationLikeReq, 0)
        _Buffer = JceWriter().write_map({'like': {
            'NS_MOBILE_OPERATION.operation_like_req': OperationLikeReq
        }, 'hostuin': {'int64': int64}}, 0)
        return _Buffer

    BusiBuff = _operation_like_req()
    Upstream = createQmfUpstream(info, 1, BusiBuff, 'QzoneNewService.like')
    Buffer = PackHead_QMF(info, 'SQQzoneSvc.like', Upstream)
    return Buffer




def SQQzoneSvc_like_rsp(Buffer: bytes):
    rsp_Buffer, msg, ret = UnQmfDownstream(Buffer, 'like', 'NS_MOBILE_OPERATION.operation_like_rsp')
    if rsp_Buffer == b'':
        return {'Busi': {}, 'msg': msg, 'ret': ret}
    like_rsp = JceReader(rsp_Buffer).read_object(operation_like_rsp)
    return {'Busi': like_rsp.to_dict(), 'msg': msg, 'ret': ret}


if __name__ == '__main__':
    pass
