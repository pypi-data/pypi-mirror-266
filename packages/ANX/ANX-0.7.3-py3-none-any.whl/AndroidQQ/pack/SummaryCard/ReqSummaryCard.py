# struct SummaryCard;
import json
import zlib

from Jce import JceInputStream, JceStruct
from Jce_b import JceWriter, JceReader

from AndroidQQ.struct import PackHeadNoToken, Pack_, Un_jce_Head
from AndroidQQ.struct.SummaryCard import ReqSummaryCard


def SummaryCard_ReqSummaryCard(info, Buffer):
    """获取摘要卡"""

    Buffer = JceWriter().write_jce_struct(Buffer, 0)

    Buffer = JceWriter().write_map({'ReqHead': bytes.fromhex('0A 00 02 0B'), 'ReqSummaryCard': Buffer},
                                   0)  # 似乎新版有更多的验证,因此用旧的头部

    Buffer = PackHeadNoToken(info, Buffer, 'SummaryCard.ReqSummaryCard',
                             'SummaryCardServantObj', 'ReqSummaryCard')
    Buffer = Pack_(info, Buffer, Types=11, encryption=1, sso_seq=info.seq)
    return Buffer


def SummaryCard_ReqSummaryCard_rsp(Buffer):
    if Buffer[0] == 120:
        Buffer = zlib.decompress(Buffer)

    data = Un_jce_Head(Buffer)
    _map = JceReader(data).read_map(0)
    _dict = _map.get('RespSummaryCard', None)
    if _dict is None:
        return None
    # 包体太大了,自动解析
    RespSummaryCard = _dict['SummaryCard.RespSummaryCard']
    stream = JceInputStream(RespSummaryCard)
    jce = JceStruct()
    jce.read_from(stream)
    return json.loads(jce.to_json())


if __name__ == '__main__':
    pass
