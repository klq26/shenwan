# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import requests
import grequests

from configManager import configManager

class swindex_holding:

    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.cm = configManager()
        pass

    def get_index_holding(self):
        """
        用申万 28 行业表示指数基金的持仓金额
        """
        print('获取指数基金持仓数据..')
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
        df_groupby.to_csv(os.path.join(self.folder, 'sw_holdings', 'category3_holding.csv'), sep='\t')
        
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
        results_df.to_csv(os.path.join(self.folder, 'sw_holdings', 'sw_index_holding.csv'), sep='\t')
        return results_df

    def get_plan_holding(self):
        """
        用申万 28 行业表示，第三方投资组合中可得知的股票比例部分。
        """
        print('获取第三方组合行业持仓数据..')
        req_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
        holding_money = round(self.cm.config['plan_holding']['klq'] + self.cm.config['plan_holding']['parents'], 2) # 1226276.81
        
        # 1. 读取计划中的持仓数据
        plan_funds = []
        response = requests.get('https://danjuanapp.com/djapi/plan/position/detail?plan_code=CSI1019', headers=req_header)
        if response and response.status_code == 200:
            fundlist = response.json()['data']['items']
            for x in fundlist:
                # 只要持仓大于 0 的基金
                if x['percent'] > 0:
                    plan_funds.append(pd.Series(x))
        else:
            print(response.status_code)
            exit(1)
        df = pd.DataFrame(plan_funds)
        df = df.drop(['type_desc','type', 'total_gain_rate'], axis=1)
        df['holding_money'] = round(df.percent / 100 * holding_money, 2)
        # print(df)

        # 2. 每只基金的股票持仓
        detail_holder = u'https://danjuanapp.com/djapi/fund/detail/'
        df_stock_list = []
        for x in df.itertuples():
            # print(x)
            response = requests.get(detail_holder + x[1], headers = req_header)
            if response and response.status_code == 200:
                stock_list = response.json()['data']['fund_position']['stock_list']
                # bond_list = response.json()['data']['fund_position']['bond_list']
                df_stocks = pd.DataFrame(stock_list)
                # 去掉港股（港股的 percent 是 NaN）
                df_stocks = df_stocks.dropna()
                df_stocks['fund_code'] = x[1]
                df_stocks['fund_name'] = x[2]
                df_stocks['fund_percent'] = x[3]
                df_stocks['fund_holding'] = x[4]
                df_stocks = df_stocks.rename(columns={'code': 'stock_code','name':'stock_name','percent':'stock_percent'})
                df_stocks['stock_holding'] = round(df_stocks['fund_holding'] * df_stocks['stock_percent'] / 100, 2)
                df_stocks = df_stocks.drop(['amarket', 'change_percentage', 'current_price', 'xq_symbol', 'xq_url'], axis=1)
                df_stocks = df_stocks[['fund_code','fund_name', 'fund_percent', 'fund_holding', 'stock_code','stock_name','stock_percent','stock_holding']]
                # 去掉持仓市值为 0 的持仓
                df_stocks = df_stocks[df_stocks['stock_holding'] > 1]
                df_stock_list.append(df_stocks)
        df_plan_holding = pd.concat(df_stock_list, ignore_index=True)
        # 保存最完整的计划数据
        # fund_code  fund_name  fund_percent  fund_holding stock_code stock_name  stock_percent  stock_holding
        # 0     007749  民生加银鹏程混合C         20.54     251877.26     002475       立讯精密           0.96        2418.02
        df_plan_holding.to_csv(os.path.join(self.folder, 'sw_holdings', 'plan365_holding.csv'), sep='\t')

        # 3. 按股票名整合
        df_groupby = df_plan_holding.groupby(['stock_code','stock_name']).sum()
        df_groupby = df_groupby.drop(['fund_percent','fund_holding','stock_percent'], axis=1)

        # 4. 增加行业情况
        df_sw = pd.read_csv(os.path.join(self.folder, 'sw_industry_categorys.csv'), sep='\t', index_col = 0)
        df_with_industry = pd.merge(left=df_groupby, right=df_sw, how='left',left_on='stock_name', right_on='display_name')
        df_with_industry = df_with_industry[['sw1_code', 'sw1_name', 'display_name', 'stock_holding']]
        df_with_industry['sw1_name'] = df_with_industry.sw1_name.apply(lambda x: x.replace('I',''))

        # 按申万 28 行业来算
        df_industry_groupby = df_with_industry.groupby(['sw1_code','sw1_name']).sum()
        total_holding = df_industry_groupby.stock_holding.sum()
        df_industry_groupby = df_industry_groupby.rename(columns={'stock_holding': 'holding_money'})
        df_industry_groupby['holding_money'] = df_industry_groupby.holding_money.apply(lambda x: round(x, 2))
        df_industry_groupby['rate'] = round(df_industry_groupby.holding_money / total_holding * 100, 2)
        df_industry_groupby['rate'] = df_industry_groupby.rate.apply(lambda x: str(x) + '%')
        df_industry_groupby.to_csv(os.path.join(self.folder, 'sw_holdings', 'sw_plan_holding.csv'), sep='\t')
        # sw1_code	sw1_name	holding_money	rate
        # 801010	农林牧渔	12380.52	1.91%
        return df_industry_groupby

    def update_sw_index_holding(self):
        # 指数基金部分的股票持仓
        df1 = self.get_index_holding()
        # df1 的 sw1_code 是 int64 类型，如果不改成字符串，merge 会出问题
        # 思路是，先取消 sw1_code 的 index 身份，全部改成字符串，再恢复 sw1_code 和 sw1_name 的身份
        df1 = df1.reset_index(drop=False)
        df1.sw1_code = df1.sw1_code.apply(lambda x: str(x))
        df1 = df1.set_index(['sw1_code','sw1_name'], drop=True)
        df1 = df1.drop(['rate'], axis=1)

        # 投资组合部分的股票持仓
        df2 = self.get_plan_holding()
        df2 = df2.drop(['rate'], axis=1)

        df = pd.merge(left=df1, right=df2, how='left', on=['sw1_code','sw1_name'], suffixes=['_index', '_plan'])
        df = df.fillna(0)
        df['holding_money'] = round((df['holding_money_index'] + df['holding_money_plan']), 2)
        total_money = round(df['holding_money_index'].sum() + df['holding_money_plan'].sum(), 2)
        print(total_money, type(total_money))
        df['rate'] = df['holding_money'].apply(lambda x : str(round(x / total_money * 100, 2)) + '%')
        df.to_csv(os.path.join(self.folder, 'sw_holdings', 'sw_holding.csv'), sep='\t')
        
       
        pass

if __name__ == "__main__":
    ih = swindex_holding()
    ih.update_sw_index_holding()
    pass