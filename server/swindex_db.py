# -*- coding: utf-8 -*-
import os
import sys
import json
import pymysql

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from server.account import account

class swindex_db:
    """
    申万数据的数据库对接适配器
    """
    def __init__(self):
        # 取用户名密码
        self.account = account()
        # 打开数据库
        self.ip_address = '112.125.25.230'
        # 给 pandas 用的引擎
        self.engine = create_engine('mysql+pymysql://{0}:{1}@{2}/shenwan'.format(self.account.mysql_user, self.account.mysql_password, self.ip_address))
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.value_file_path = os.path.join(self.folder, 'sw_history_daily_price.csv')
        self.eval_file_path = os.path.join(self.folder, 'sw_history_daily_eval.csv')
        pass
    
    def swindex_df_to_db(self, df, name):
        """
        DataFrame 存入阿里云数据库表
        """
        # DataFrame.to_sql(name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, type=None, method=None)
        df.to_sql(name = name, con = self.engine, if_exists='replace', index=False)
        pass

    def swindex_df_from_db(self, name):
        """
        从阿里云数据库表中读取数据并返回 DataFrame
        """
        # sql = u"SELECT * FROM {0} WHERE ACCOUNT LIKE '%%{1}%%'".format(name, account)
        sql = u"SELECT * FROM {0}".format(name)
        df = pd.read_sql(sql, self.engine)
        return df

    def swindex_value_to_db(self):
        """
        [shortcut] 申万日线数据存入阿里云服务器
        """
        df = pd.read_csv(self.value_file_path, sep='\t', index_col=0)
        print('申万日线数据写入阿里云服务器数据库...')
        self.swindex_df_to_db(df, 'daily_price')
        pass

    def swindex_eval_to_db(self):
        """
        [shortcut] 申万日估值数据存入阿里云服务器数据库
        """
        df = pd.read_csv(self.eval_file_path, sep='\t', index_col=0)
        print('申万估值数据写入阿里云服务器数据库...')
        self.swindex_df_to_db(df, 'daily_eval')
        pass

if __name__ == "__main__":
    sw_db = swindex_db()
    # sw_db.swindex_value_to_db()
    # sw_db.swindex_eval_to_db()