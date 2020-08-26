# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import requests

class index_holding:

    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        pass

    def get_index_holding(self):
        """
        用申万 28 行业表示持仓金额
        """
        # 0. 准备工作：支持用申万 28 行业表达的三级分类列表
        indexs = pd.read_csv(os.path.join(self.folder, 'index_weight_list.csv'), sep='\t', index_col=0)
        support_list = indexs.name.tolist()
        # 1. 取持仓数据
        fundlist = None
        response = requests.get('https://www.klq26.site/familyholding/api/fundholding')
        if response and response.status_code == 200:
        #     {
        #         "category1": "A 股",
        #         "categoryId": 111,
        #         "holding_money": 6185.58,
        #     },
            fundlist = response.json()['data']
        
        # 2. 生成 series 数组，最终生成 dataframe，供分析
        obj_list = []
        for fund in fundlist:
            # dict 直接生产 Series 对象
            series = pd.Series(fund)
            obj_list.append(series)
        # Series 数组直接生成 DataFrame 对象
        df = pd.DataFrame(obj_list)
        df = df[['category3','categoryId', 'holding_money']]
        df = df[df.category3.isin(support_list)]
        df_groupby = df.groupby(['categoryId', 'category3']).sum()
        # 得到每个三级分类的持仓金额（后续用申万 28 行业表达）
        df_groupby = df_groupby.sort_values(['categoryId'])
        df_groupby['holding_money'] = df_groupby['holding_money'].apply(lambda x : round(x, 2))
        df_groupby.to_csv(os.path.join(self.folder, 'index_holding', 'category3_holding.csv'), sep='\t')
        
        # 3. 读取申万 28 行业权重表，计算每个申万行业的持仓金额
        df_weight = pd.read_csv(os.path.join(self.folder, 'index_weights', 'all_index_sw_weights.csv'), sep='\t', index_col=[0,1], header=[0,1])
        results_df = pd.DataFrame(index=df_weight.index)
        # 去持仓数据中迭代每一个三级分类
        for x in df_groupby.itertuples():
            # 名称
            category3 = x[0][1]
            # 持仓金额
            money = round(x.holding_money, 2)
            # 去指数申万权重库里寻找
            Found = False
            for y in df_weight.columns:
                if y[1] == category3:
                    weights = df_weight[y[0], y[1]]
                    results_df[category3] = round(weights / 100 * money, 2)
                    Found = True
                    break
            if not Found:
                print(category3)
        # 行业转置
        results_df = results_df.T.sum()
        # 总金额数
        total_money = round(results_df.sum(), 2)
        holding_rate = round(results_df / total_money * 100, 2)
        results_df = pd.DataFrame([results_df, holding_rate])
        results_df = results_df.T
        results_df.columns = ['holding_money','rate']
        results_df['rate'] = results_df['rate'].apply(lambda x: '{:.2f}%'.format(x))
        results_df['holding_money'] = results_df['holding_money'].apply(lambda x: round(x, 2))
        results_df.to_csv(os.path.join(self.folder, 'index_holding', 'sw_holding.csv'), sep='\t')
        return results_df

if __name__ == "__main__":
    ih = index_holding()
    df = ih.get_index_holding()
    pass