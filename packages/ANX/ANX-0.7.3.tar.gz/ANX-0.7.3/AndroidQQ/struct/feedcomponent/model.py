# package com.qzone.proxy.feedcomponent.model;
import json

from Jce import JceInputStream, JceStruct
from Jce_b import JceReader

from AndroidQQ.struct.NS_MOBILE_FEEDS.cell_comm import cell_comm
from AndroidQQ.struct.NS_MOBILE_FEEDS.cell_operation import cell_operation
from AndroidQQ.struct.NS_MOBILE_FEEDS.cell_userinfo import cell_userinfo


# def JceCellData(singlefeed: tuple):
#     buffer = singlefeed[1]
#     if singlefeed[0] == 0:
#         cell = cell_comm()  # 添加实例属性
#         cell.read_from(JceReader(buffer))
#     elif singlefeed[0] == 1:
#         cell = cell_userinfo()
#         cell.read_from(JceReader(buffer))
#
#     else:
#         # 自动解析
#         stream = JceInputStream(buffer)
#         jce_wup = JceStruct()
#         jce_wup.read_from(stream)
#         cell = json.loads(jce_wup.to_json())
#     return cell

class JceCellData:

    def __init__(self, singlefeed: dict):

        buffer = singlefeed.get(0, None)
        if buffer is not None:
            self.cell_comm = cell_comm()  # 添加实例属性
            self.cell_comm.read_from(JceReader(buffer))

        buffer = singlefeed.get(1, None)
        if buffer is not None:
            self.cell_userinfo = cell_userinfo()
            self.cell_userinfo.read_from(JceReader(buffer))

        buffer = singlefeed.get(18, None)
        if buffer is not None:
            self.cell_operation = cell_operation()
            self.cell_operation.read_from(JceReader(buffer))
