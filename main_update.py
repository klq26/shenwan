# -*- coding: utf-8 -*-

import os
import sys

from server.swindex_eval import swindex_eval
from server.swindex_value import swindex_value
from server.index_weight import index_weight

class main_update:
    """
    获取和申万 28 行业有关的数据（指数走势、指数等权估值及百分位等）
    """
    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        pass

if __name__ == "__main__":
    # 更新估值
    eval = swindex_eval()
    eval.update_history_daily_eval()
    # 更新点数
    val = swindex_value()
    val.update_history_daily_price()
    # 更新指数行业权重
    weight = index_weight()
    weight.update_index_weights()
    pass