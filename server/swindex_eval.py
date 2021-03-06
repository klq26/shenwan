# -*- coding: utf-8 -*-

import os
import sys
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from jqdatasdk import *

from server.configManager import configManager
from server.account import account
from server.swindex_db import swindex_db

pd.set_option('display.max_columns',30)
pd.set_option('display.width',180)
# 登录查看剩余条目
ac = account()
auth(ac.joinquant_user, ac.joinquant_password)

"""
1、新版行业分类标准设立一级行业 28 个、二级行业 104 个、三级行业 227 个。
2、一级行业调整包括:
    2.1 分拆建筑建材为建筑材料、建筑装饰;
        注释：1 变 2
    2.2 分拆机械设备为电气设备、机械设备;
        注释：1 变 2
    2.3 分拆交运设备为国防军工、汽车(其中铁路设备纳入新“机械设备”一级行业);
        注释：1 变 2
    2.4 信息设备、信息服务调整为计算机、传媒、通信。
        注释：2 变 3
    2.5 分拆金融服务为银行、非银金融;
    2.6 更名黑色金属、餐饮旅游为钢铁、休闲服务。下属二、三级行业分类均相应调整。
        注释：聚宽已经把 2014 年以前的改名啦，此处无需修改。
    总结一下，就是 23 拆成 28，
3、聚宽数据上，从 2014-02-21 开始行业数达到了 27，2014-02-24 后开始都是28行业，2014-02-20 还是 23 个行业
"""
class swindex_eval:
    """
    更新申万 28 行业指数的日线历史估值走势数据
    """
    def __init__(self):
        print(get_query_count())
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.cm = configManager()
        self.data_column = ['date', 'sw1_code', 'sw1_name', 'total_count', 'pe' ,'pe_negative_count', 'pe_over_125_count', 'pb']
        self.end_date = datetime.today().replace(hour=0, minute=0, second=0,microsecond=0) - timedelta(days=1)
        # 最新的股票池（online）
        self.latest_all_securities_df = self.get_all_stocks(start_date = self.end_date)
        # 填充行业分类（local）
        self.local_industry_database_df = pd.read_csv(os.path.join(self.folder, u'sw_industry_categorys.csv'), sep='\t',encoding=u'utf-8', index_col=0)
        pass

    def get_industry_for_stocks(self, df):
        """
        为股票样本池，补充申万行业分类数据
        """
        # return pd.read_csv(os.path.join(self.folder, 'sw_industry_categorys.csv'), sep='\t', index_col=0)
        results = get_industry(security = list(df.index))
        # {'000001.XSHE': {'jq_l1': {'industry_code': 'HY007', 'industry_name': '金融指数'},
        #                  'jq_l2': {'industry_code': 'HY493', 'industry_name': '多元化银行指数'},
        #                  'sw_l1': {'industry_code': '801780', 'industry_name': '银行I'},
        #                  'sw_l2': {'industry_code': '801192', 'industry_name': '银行II'},
        #                  'sw_l3': {'industry_code': '851911', 'industry_name': '银行III'},
        #                  'zjw': {'industry_code': 'J66', 'industry_name': '货币金融服务'}
        #                 },
        # 申万一二三级行业代码及名称占位
        df.loc[:, 'sw1_code'] = 'code'
        df.loc[:, 'sw1_name'] = 'name'
        df.loc[:, 'sw2_code'] = 'code'
        df.loc[:, 'sw2_name'] = 'name'
        df.loc[:, 'sw3_code'] = 'code'
        df.loc[:, 'sw3_name'] = 'name'
        idx = 1
        for k, v in results.items():
            # print(idx, k, v.get('sw_l1', '未知'))
            # .loc 是按 label 选择，k 是指数代码。iloc 是按行号选择 df.iloc[1] 是第一行
            # ★注意：使用 DafaFrameming.loc[行名, 列名] = 值 的方式去赋值, 而不是使用DataFrame[][]的形式去赋值，后者会出现 warning 和不知道修改的是 copy 还是 视图 的问题。
            # 部分退市股票，如 300216.XSHE 千山药机，现在叫千山退是无法查到行业分类的。下面 get 函数给出兜底
            df.loc[k, 'sw1_code'] = v.get('sw_l1', {'industry_code': '获取失败'})['industry_code']
            df.loc[k, 'sw2_code'] = v.get('sw_l2', {'industry_code': '获取失败'})['industry_code']
            df.loc[k, 'sw3_code'] = v.get('sw_l3', {'industry_code': '获取失败'})['industry_code']
            df.loc[k, 'sw1_name'] = v.get('sw_l1', {'industry_name': '获取失败'})['industry_name']
            df.loc[k, 'sw2_name'] = v.get('sw_l2', {'industry_name': '获取失败'})['industry_name']
            df.loc[k, 'sw3_name'] = v.get('sw_l3', {'industry_name': '获取失败'})['industry_name']
            idx += 1
        # # failed_df = df[df['sw1_code'] == '获取失败']
        # # 写本地（注意这个 sort 要到给完 pe 估值才好搞，要不然 pe 返回数据是无法按 industry 升序排列的）
        df = df.sort_values(by=['sw1_code','sw2_code','sw3_code'])
        # df.to_csv(os.path.join(self.folder, 'sw_industry_categorys.csv'), sep='\t')
        return df

    def get_all_stocks(self, start_date):
        """
        获取聚宽全部股票作为样本池（包含已经退市的股票，这部分无法获得行业信息，可忽略），返回 DataFrame 对象
        """
        # return pd.read_csv('all_securities.csv', sep='\t', index_col=0)

        # 国证A股指数的样本股为在深圳、上海证券交易所上市的除ST、*ST股票外的所有A股，用以反映中国A股市场股票价格的总体变动趋势，向市场提供全面有效的标尺和业绩比较基准。
        # all_stocks_without_st = get_index_stocks('399317.XSHE')
        # 获取聚宽支持的所有股票（这一步主要是拿到所有股票的 display_name，get_index_stocks 仅拿到 indexs list）
        df = get_all_securities(date=start_date)
        # 去掉无用列 type = stock，name 是缩写，和 index 列名称冲突，忽略。
        df = df.drop(['type', 'name'], axis=1)
        # 去掉国证A指以外的股票 && 去掉 ST
        # df = df_all_stocks_in_joinQuant[(df_all_stocks_in_joinQuant.index.isin(all_stocks_without_st)) & (~df_all_stocks_in_joinQuant['display_name'].str.contains('ST', case=False))]
        return df

    def get_all_securities_industry_from_db(self, df):
        """
        从本地最新一日的“申万行业分类” 数据中，为历史日股票池列表，补充行业数据
        """
        future_df = self.local_industry_database_df
        sub_future_df = future_df[future_df.index.isin(df.index)]
        df = sub_future_df[~(sub_future_df['sw1_code'] == '获取失败')]
        return df

    def get_all_stocks_eval(self, df, start_date):
        """
        为股票样本池，补充估值数据
        """
        q = query(
            valuation.code,
            valuation.pe_ratio,
            valuation.pb_ratio
        ).order_by(
            valuation.code.asc()
        ).filter(
            valuation.code.in_(list(df.index))
        )
        evals = get_fundamentals(q, start_date)
        # 数据表也按股票代码升序排列
        df = df.sort_index()
        df['pe'] = list(evals.pe_ratio.astype(float))
        df['pb'] = list(evals.pb_ratio.astype(float))
        df = df.sort_values(by=['sw1_code','sw2_code','sw3_code'])
        return df

    def calc_equal_weight_eval(self, df, start_date):
        """
        以等权法，计算 28 个申万行业以及全市场各自的市盈率、市净率等数据
        """
        results_df = pd.DataFrame(columns = self.data_column)
        count = 0
        # 市盈率大于 125 倍
        pe_over_125_df = df[df.pe >= 125]
        # 市盈率为负数
        pe_negative_df = df[df.pe <= 0]
        # 市盈率符合要求的结果 (0 < pe < 125)
        pe_ok_df = df[(~df.index.isin(pe_over_125_df.index)) & (~df.index.isin(pe_negative_df.index))]
        # print(len(df), len(pe_over_125_df), len(pe_negative_df), len(pe_ok_df))
        
        # 指数市盈率（公式：PE = n/Σ[1/个股PE]，n为PE个数），市净率 PB 算法相同
        temp_pe_ok_df = pe_ok_df.copy()
        temp_pe_ok_df.loc[:, 'one_over_pe'] = pe_ok_df.loc[:, 'pe'].copy().apply(lambda x : 1 / x)
        temp_df = df.copy()
        temp_df.loc[:, 'one_over_pb'] = df['pb'].apply(lambda x : 1 / x)
        all_stock_equal_weight_pe = round(len(pe_ok_df) / temp_pe_ok_df.one_over_pe.sum(), 2)
        all_stock_equal_weight_pb = round(len(df) / temp_df.one_over_pb.sum(), 2)
        # 全市场 - 申万A指
        results_df = results_df.append(pd.Series(data=[start_date, '801003','申万A指',len(df), all_stock_equal_weight_pe, len(pe_negative_df), len(pe_over_125_df), all_stock_equal_weight_pb],name=count, index=self.data_column))
        count += 1
        # 28 行业
        sw1_industrys = df.sw1_name.unique()
        for industry in sw1_industrys:
            # print(industry, len(sub_df))
            sub_df = df[df['sw1_name'] == industry]
            sub_pe_ok_df = pe_ok_df[pe_ok_df['sw1_name'] == industry]
            sub_pe_over_125_df = pe_over_125_df[pe_over_125_df['sw1_name'] == industry]
            sub_pe_negative_df = pe_negative_df[pe_negative_df['sw1_name'] == industry]
            
            # 指数市盈率（公式：PE = n/Σ[1/个股PE]，n为PE个数），市净率 PB 算法相同
            temp_pe_ok_df = sub_pe_ok_df.copy()
            temp_pe_ok_df.loc[:, 'one_over_pe'] = sub_pe_ok_df.loc[:, 'pe'].copy().apply(lambda x : 1 / x)
            temp_df = sub_df.copy()
            temp_df.loc[:, 'one_over_pb'] = sub_df['pb'].apply(lambda x : 1 / x)
            industry_pe = round(len(sub_pe_ok_df) / temp_pe_ok_df.one_over_pe.sum(), 2)
            industry_pb = round(len(sub_df) / temp_df.one_over_pb.sum(), 2)
            results_df = results_df.append(pd.Series(data=[start_date, sub_df.loc[:, 'sw1_code'].values[0],industry.replace('I',''),len(sub_df), industry_pe, len(sub_pe_negative_df), len(sub_pe_over_125_df), industry_pb], name=count, index=self.data_column))
            count += 1
            # break
        # print(results_df)
        return results_df

    def update_history_daily_eval(self):
        """
        更新申万 28 行业及全市场整体的日线等权历史数据
        """
        ###
        # 1. 先看是否需要更新本地申万行业分类表
        ###
        diff_df = self.latest_all_securities_df[~(self.latest_all_securities_df.index.isin(self.local_industry_database_df.index))].copy()
        # 说明最新股票池中，有本地行业分类数据库中没有的数据
        if len(diff_df) > 0:
            diff_industry_df = self.get_industry_for_stocks(diff_df)
            print('新入库行业分类数据：\n\n{0}'.format(diff_industry_df))
            self.local_industry_database_df = self.local_industry_database_df.append(diff_industry_df)
            self.local_industry_database_df = self.local_industry_database_df.sort_values(by=['sw1_code','sw2_code','sw3_code'])
            self.local_industry_database_df.to_csv(os.path.join(self.folder, 'sw_industry_categorys.csv'), sep='\t')
        
        ###
        # 2. 拿出之前计算的数据，更新 start_date
        ###
        
        # 预加载以前拿到的数据
        file_path = os.path.join(self.folder, 'sw_history_daily_eval.csv')
        results_df = None
        # 估值数据是从 2005-02-03 开始的
        start_date = datetime.strptime('2005-02-03', '%Y-%m-%d')
        if os.path.exists(file_path):
            results_df = pd.read_csv(file_path, sep='\t', index_col=0)
            if len(results_df) > 0:
                # 更新起始日期
                last_date = results_df.tail(1).date.values[0]
                # 库中最后一天的下一天
                start_date = datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            results_df = pd.DataFrame()
        
        ###
        # 3. 如果终止日期大于起始日期，且二者之间存在交易日时，本次更新才有意义
        ###
        
        if self.end_date >= start_date:
            trade_days = get_trade_days(start_date = start_date, end_date = self.end_date)
            print(trade_days, len(trade_days))
            day_to_write_interval = 5
            day_count = 0
            for current_date in trade_days:
                date_str = current_date.strftime('%Y-%m-%d')
                print(f'计算：{date_str}')
                all_securities_df = self.get_all_stocks(start_date = date_str)
                all_securities_df = self.get_all_securities_industry_from_db(all_securities_df)
                all_securities_df = self.get_all_stocks_eval(df = all_securities_df, start_date = date_str)
                results_df = pd.concat([results_df, self.calc_equal_weight_eval(all_securities_df, date_str)], ignore_index=True)
                day_count += 1
                if day_count == day_to_write_interval:
                    print('写入磁盘')
                    results_df.to_csv(os.path.join(self.folder, 'sw_history_daily_eval.csv'),sep='\t')
                    day_count = 0
                # break
            print('写入磁盘')
            results_df.to_csv(os.path.join(self.folder, 'sw_history_daily_eval.csv'),sep='\t')
            # 存入阿里云服务器数据库
            swindex_db().swindex_df_to_db(results_df, 'daily_eval')
        
        ###
        # 4. 更新最新一日的等权估值情况，以便接口访问
        ###
        
        latest_eval_df = results_df[-29:]
        latest_eval_df = latest_eval_df.reset_index(drop=True)
        latest_eval_df.to_csv(os.path.join(self.folder, 'sw_latest_eval.csv'),sep='\t')
        # print(latest_eval_df)
        print(get_query_count())
        pass

if __name__ == "__main__":
    sw_eval = swindex_eval()
    sw_eval.update_history_daily_eval()
    pass

