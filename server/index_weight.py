# -*- coding: utf-8 -*-
import os
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from jqdatasdk import *

from account import account

pd.set_option('display.max_columns',30)
pd.set_option('display.width',180)
# 登录查看剩余条目
ac = account()
auth(ac.joinquant_user, ac.joinquant_password)

class index_weight:

    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.future_industry_df = pd.read_csv('最新申万行业分类.csv', sep='\t', index_col=0)
        pass

    def get_index_stock_industry(self, name, df):
        future_df = self.future_industry_df
        unknow_df = df[~(df.index.isin(future_df.index))]
        if len(unknow_df) > 0:
            print('{0} 未知成分股列表：{1}'.format(name, unknow_df))
        else:
            industry_df = future_df[future_df.index.isin(df.index)]
            industry_df = industry_df.sort_index()
            df['sw1_code'] = industry_df['sw1_code']
            df['sw1_name'] = industry_df['sw1_name']
            # 奇怪的问题，如果不加 apply，weight 后面多很多位无效数字
            df['weight'] = df.weight.apply(lambda x : round(x, 4))
        return df

    def get_index_weights(self):
        index_weight_list_df = pd.read_csv('index_weight_list.csv',sep='\t',index_col=0)
        idx = 1
        for x in index_weight_list_df.itertuples():
            # 1. 获取指数权重
            index_weight_df = get_index_weights(x.code)
            # e.g.
            # code	weight	display_name	date
            # 000008.XSHE	0.107	神州高铁	2020-08-14
            order = ['display_name', 'date', 'weight']
            index_weight_df = index_weight_df[order]
            index_weight_df = index_weight_df.sort_index()
            # index_weight_df.to_csv('index_weights/{0}_{1}_{2}.csv'.format(idx, x.code, x.name), sep='\t',encoding='utf-8')
            # index_weight_df = pd.read_csv('index_weights/{0}_{1}_{2}.csv'.format(idx, x.code, x.name), sep='\t', index_col=0)
            
            # 2. 给指数成分股补充申万一级行业数据
            index_industry_weight_df = self.get_index_stock_industry(x.name, index_weight_df)
            index_industry_weight_df.to_csv('index_weights/{0}_{1}_{2}.csv'.format(idx, x.code, x.name), sep='\t',encoding='utf-8')
            
            # 3. 按行业整合成分股占比
            index_grouped = index_industry_weight_df.groupby(['sw1_code','sw1_name']).sum()
            index_grouped['weight'] = index_grouped.weight.apply(lambda x : round(x, 4))
            index_grouped.to_csv('index_weights/{0}_{1}_{2}_by_sw_industry.csv'.format(idx, x.code, x.name), sep='\t',encoding='utf-8')
            idx += 1
            # break
        pass

if __name__ == "__main__":
    iw = index_weight()
    iw.get_index_weights()
    pass