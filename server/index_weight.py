# -*- coding: utf-8 -*-
import os
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from jqdatasdk import *

# from server.account import account
from account import account

pd.set_option('display.max_columns',30)
pd.set_option('display.width',180)
# 登录查看剩余条目
ac = account()
auth(ac.joinquant_user, ac.joinquant_password)

class index_weight:

    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.future_industry_df = pd.read_csv(os.path.join(self.folder, 'sw_industry_categorys.csv'), sep='\t', index_col=0)
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

    def update_index_weights(self):
        idx = 1
        # columns
        df_index = pd.read_csv(os.path.join(self.folder, 'index_weight_list.csv'),sep='\t',index_col=0)
        # df_index_temp.code = df_index.code.apply(lambda x : x.split('.')[0])
        df_index_temp = df_index.set_index(['code','name'], drop=True)
        columns = df_index_temp.T.columns
        # index
        df_sw = pd.read_csv(os.path.join(self.folder, 'sw_industry_list.csv'), sep='\t')
        index = pd.MultiIndex.from_arrays([df_sw.sw1_code.values.tolist(), df_sw.sw1_name.values.tolist()], names=['sw1_code','sw1_name'])
        # x 轴：指数 y 轴：申万行业
        # dataframe
        df = pd.DataFrame(index=index, columns=columns)
        df = df.fillna(0.000)
        for x in df_index.itertuples():
            print(f'获取 {x.name} ...')
            # 1. 获取指数权重
            df_weight = get_index_weights(x.code)
            # e.g.
            # code	weight	display_name	date
            # 000008.XSHE	0.107	神州高铁	2020-08-14
            order = ['display_name', 'date', 'weight']
            df_weight = df_weight[order]
            df_weight = df_weight.drop(['date'], axis=1)
            df_weight = df_weight.sort_index()

            # 2. 给指数成分股补充申万一级行业数据
            df_weight_industry = self.get_index_stock_industry(x.name, df_weight)
            df_weight_industry.to_csv(os.path.join(self.folder, 'index_weights/{0}_{1}_{2}.csv'.format(str(idx).zfill(2), x.code, x.name)), sep='\t',encoding='utf-8')

            # 3. 按行业整合成分股占比
            df_grouped = df_weight_industry.groupby(['sw1_code','sw1_name']).sum()
            # TODO 这样做，二维 index 会覆盖成一维，虽然 Series 相加的操作成功了，但是还有隐患，应该可以为每个 index level 单独设置 dtype 才对
            df_grouped['weight'] = df_grouped.weight.apply(lambda x : round(x, 4))
            df_grouped.to_csv(os.path.join(self.folder, 'index_weights/{0}_{1}_{2}_sw.csv'.format(str(idx).zfill(2), x.code, x.name)), sep='\t',encoding='utf-8')
            
            # 4. 存入磁盘后，修改 index 为 int64，好与 df 的 Series 因为共同的 index 列而相加
            df_grouped.index = df_grouped.index.levels[0].astype('int64')
            df[x.code, x.name] += df_grouped.weight
        df = df.fillna(0.000)
        # 5. 数组整合表
        df.to_csv(os.path.join(self.folder, 'index_weights/all_index_sw_weights.csv'), sep='\t',encoding='utf-8')
        return df

if __name__ == "__main__":
    iw = index_weight()
    iw.update_index_weights()
    pass