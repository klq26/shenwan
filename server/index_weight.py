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
        self.future_industry_df = pd.read_csv(os.path.join(self.folder, '最新申万行业分类.csv'), sep='\t', index_col=0)
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
            df['sw1_name'] = df.sw1_name.apply(lambda x : x.replace('I',''))
        return df

    def get_index_weights(self):
        index_weight_list_df = pd.read_csv(os.path.join(self.folder, 'index_weight_list.csv'),sep='\t',index_col=0)
        idx = 1
        # x 轴：指数 y 轴：申万行业
        industry_index_df = pd.read_csv(os.path.join(self.folder, 'sw_industry_list.csv'), sep='\t', index_col=0)
        for x in index_weight_list_df.itertuples():
            # 1. 获取指数权重
            index_weight_df = get_index_weights(x.code)
            # e.g.
            # code	weight	display_name	date
            # 000008.XSHE	0.107	神州高铁	2020-08-14
            order = ['display_name', 'date', 'weight']
            index_weight_df = index_weight_df[order]
            index_weight_df = index_weight_df.sort_index()
            
            # 2. 给指数成分股补充申万一级行业数据
            index_industry_weight_df = self.get_index_stock_industry(x.name, index_weight_df)
            index_industry_weight_df.to_csv(os.path.join(self.folder, 'index_weights/{0}_{1}_{2}.csv'.format(str(idx).zfill(2), x.code, x.name)), sep='\t',encoding='utf-8')
            
            # 3. 按行业整合成分股占比
            index_grouped = index_industry_weight_df.groupby(['sw1_code','sw1_name']).sum()
            index_grouped['weight'] = index_grouped.weight.apply(lambda x : round(x, 4))
            index_grouped.to_csv(os.path.join(self.folder, 'index_weights/{0}_{1}_{2}_by_sw_industry.csv'.format(str(idx).zfill(2), x.code, x.name)), sep='\t',encoding='utf-8')
            # 这里因为 groupby 的关系，把 sw1_code 和 sw1_name 组成了 multiIndex，必须重置 index 并只设定 sw1_code 为 index，否则下面的 isin 会很麻烦（需要判断 name.isin(index.levels[0])）
            index_grouped = index_grouped.reset_index(drop=False)
            index_grouped = index_grouped.set_index("sw1_code", drop=True)
            # groupby 之后的 index 类型是 字符串，后面无法使用 sort index 功能
            index_grouped.index = index_grouped.index.astype('int64')

            # 4. 把多指数汇总至同一张行业二维表
            non_industry_df = industry_index_df[~(industry_index_df.sw1_name.isin(index_grouped.sw1_name))]
            non_industry_df.loc[:, 'weight'] = [0.000 for x in range(len(non_industry_df))]
            print(non_industry_df.dtypes)
            index_full_df = pd.concat([index_grouped, non_industry_df])
            index_full_df['weight'] = index_full_df.weight.astype('float64')
            print(index_full_df.index)
            index_full_df = index_full_df.sort_index()
            industry_index_df[x.name] = index_full_df.weight
            idx += 1
            # break
        # 把 sw1_name 也挪成 index，从列里删除
        industry_index_df = industry_index_df.set_index("sw1_name", drop=True, append=True)
        industry_index_df.to_csv(os.path.join(self.folder, 'index_weights/all_index_sw_weights.csv'), sep='\t',encoding='utf-8')
        pass

if __name__ == "__main__":
    iw = index_weight()
    iw.get_index_weights()
    pass