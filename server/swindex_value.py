# -*- coding: utf-8 -*-
import os
import sys
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from jqdatasdk import *

from server.account import account
from server.swindex_db import swindex_db

pd.set_option('display.max_columns',30)
pd.set_option('display.width',180)
# 登录查看剩余条目
ac = account()
auth(ac.joinquant_user, ac.joinquant_password)

class swindex_value:

    def __init__(self):
        print(get_query_count())
        self.folder = os.path.abspath(os.path.dirname(__file__))
        # 申万 28 行业（因为部分行业名称在历史上发生过变化，所以用 code 来筛选数据是最可靠的）
        self.sw1_codes = [801010, 801020, 801030, 801040, 801050, 801080, 801110, 801120, 801130, 801140, 801150, 801160, 801170, 801180, 801200, 801210, 801230, 801710, 801720, 801730, 801740, 801750, 801760, 801770, 801780, 801790, 801880, 801890]
        pass

    def update_history_daily_price(self):
        """
        获取申万 28 行业的历史指数日线数据
        """
        # 计算开始日期
        file_path = os.path.join(self.folder, 'sw_history_daily_price.csv')
        results_df = None
        # 估值数据是从 2005-02-03 开始的
        start_date = '2005-02-03'
        # 创建一个 00:00:00 的日期，如 2020-08-14 00:00:00
        end_date = datetime.today().replace(hour=0, minute=0, second=0,microsecond=0)

        if os.path.exists(file_path):
            results_df = pd.read_csv(file_path, sep='\t', index_col=0, parse_dates=True)
            if len(results_df) > 0:
                # 更新起始日期
                last_date = results_df.tail(1).date.values[0]
                # 库中最后一天的下一天
                start_date = datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            results_df = pd.DataFrame()
        # end_date 由于接口一次性最多返回 4000 条，按每天 28 条（申万 28）计算，一次拿 140 天比较稳健（140 * 28 = 3920）
        if end_date >= start_date:
            trade_days = get_trade_days(start_date = start_date, end_date = end_date)
            day_to_query_interval = 140
            for i in range(0, len(trade_days), day_to_query_interval):
                if i + day_to_query_interval < len(trade_days):
                    start_date = trade_days[i]
                    end_date = trade_days[i + day_to_query_interval - 1]
                else:
                    start_date = trade_days[i]
                    end_date = trade_days[-1]
                print(start_date, end_date)
                # query
                q = query(
                    finance.SW1_DAILY_PRICE
                    ).filter(
                        finance.SW1_DAILY_PRICE.code.in_(self.sw1_codes),
                        finance.SW1_DAILY_PRICE.date >= start_date,
                        finance.SW1_DAILY_PRICE.date <= end_date,
                    )
                df = finance.run_query(q)
                df = df.drop(['id'], axis=1)
                # code 统一成数字类型，date 改成字符串，便于和库内数据排序
                df.code = df.code.astype('int64')
                dates= df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
                df['date'] = dates
                # 清洗数据（有 0.000000079 这样的尾巴）
                df['open']= df['open'].apply(lambda x: round(x, 2))
                df['high']= df['high'].apply(lambda x: round(x, 2))
                df['low']= df['low'].apply(lambda x: round(x, 2))
                df['close']= df['close'].apply(lambda x: round(x, 2))
                df['volume']= df['volume'].apply(lambda x: round(x, 2))
                df['money']= df['money'].apply(lambda x: round(x, 2))
                results_df = pd.concat([results_df, df], ignore_index=True)
                # results_df.to_csv(file_path,sep='\t')
                # break
        # 排序（先日期，再行业代码）
        results_df = results_df.sort_values(['date','code'])

        # 改名（电子元器件 => 电子，餐饮旅游 => 休闲服务）
        results_df['name']= results_df['name'].apply(lambda x: x.replace('电子元器件','电子').replace('餐饮旅游', '休闲服务'))
        results_df = results_df.reset_index()
        # 存入本地文件
        results_df.to_csv(file_path,sep='\t',index=0)
        # print(results_df)
        # 存入阿里云服务器数据库
        swindex_db().swindex_df_to_db(results_df, 'daily_price')
        pass

if __name__ == "__main__":
    sw_value = swindex_value()
    sw_value.update_history_daily_price()
    pass

