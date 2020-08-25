# -*- coding: utf-8 -*-

import os
import sys
import json
import time
from datetime import datetime
from datetime import timedelta

import grequests
import pandas as pd

from server.configManager import configManager

class swindex:
    """
    获取和申万 28 行业有关的数据（指数走势、指数等权估值及百分位等）
    """
    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.cm = configManager()
        pass

    def get_sw_index_eval(self):
        """
        获取申万 28 行业，以及申万全 A 的指数估值
        """
        # 最新一日
        self.lastest_eval_df = pd.read_csv(os.path.join(self.folder, 'sw_latest_eval.csv'),sep='\t',index_col=0)
        # 历史永续数据库
        all_eval_df = pd.read_csv(os.path.join(self.folder, 'sw_history_daily_eval.csv'),sep='\t',index_col=0)
        #     "history": {
        #     "top_dates": ["2007-05-28", "2010-04-14", "2015-06-08"],
        #     "bottom_dates": ["2008-11-04", "2012-12-04", "2018-11-01"]
        # }
        ultimate_values = {'to_tops': [], 'to_bottoms': []}
        lastest_pe = self.lastest_eval_df[self.lastest_eval_df.sw1_code == 801003].pe.values[0]
        lastest_pb = self.lastest_eval_df[self.lastest_eval_df.sw1_code == 801003].pb.values[0]
        # print(lastest_pe, lastest_pb)
        # 大顶
        top_dates = self.cm.config['history']['top_dates']
        tops_df = all_eval_df[(all_eval_df.date.isin(top_dates)) & (all_eval_df.sw1_code == 801003)]
        for x in tops_df.itertuples():
            # print(x.pe, x.pb)
            distance = {}
            distance['date'] = x.date
            distance['pe'] = x.pe
            distance['pb'] = x.pb
            distance['pe_distance'] = str(round((x.pe / lastest_pe - 1) * 100, 2)) + '%'
            distance['pb_distance'] = str(round((x.pb / lastest_pb - 1) * 100, 2)) + '%'
            ultimate_values['to_tops'].append(distance)
        # 大底
        bottom_dates = self.cm.config['history']['bottom_dates']
        bottom_df = all_eval_df[(all_eval_df.date.isin(bottom_dates)) & (all_eval_df.sw1_code == 801003)]
        for x in bottom_df.itertuples():
            # print(x.pe, x.pb)
            distance = {}
            distance['date'] = x.date
            distance['pe'] = x.pe
            distance['pb'] = x.pb
            distance['pe_distance'] = str(round((x.pe / lastest_pe - 1) * 100, 2)) + '%'
            distance['pb_distance'] = str(round((x.pb / lastest_pb - 1) * 100, 2)) + '%'
            ultimate_values['to_bottoms'].append(distance)
        # print(ultimate_values)

        # 以 tuples 模式迭代
        datalist = []
        for eval in self.lastest_eval_df.itertuples():
            item = dict()
            item['sw1_code'] = eval.sw1_code
            item['sw1_name'] = eval.sw1_name
            item['date'] = eval.date
            item['total_count'] = eval.total_count
            item['pe'] = eval.pe
            item['pe_negative_count'] = eval.pe_negative_count
            item['pe_over_125_count'] = eval.pe_over_125_count
            item['pb'] = eval.pb
            # 按行业取出全部数据
            industry_all_eval_df = all_eval_df[all_eval_df.sw1_code == eval.sw1_code]
            df = industry_all_eval_df
            # 永续 pe & pb 估值百分位
            pe_percentile = round(len(df[df['pe'] <= eval.pe]) / len(df) * 100, 2)
            item['pe_percentile'] = str(pe_percentile) + '%'
            pb_percentile = round(len(df[df['pb'] <= eval.pb]) / len(df) * 100, 2)
            item['pb_percentile'] = str(pb_percentile) + '%'
            # 最近 3 年 pe & pb 估值百分位
            end_date = datetime.strptime(eval.date, '%Y-%m-%d')
            y3_start_date = end_date - timedelta(days=365 * 3)
            y3_df = df[df.date >= y3_start_date.strftime('%Y-%m-%d')].copy()
            pe_percentile_3y = round(len(y3_df[y3_df['pe'] <= eval.pe]) / len(y3_df) * 100, 2)
            item['pe_percentile_3y'] = str(pe_percentile_3y) + '%'
            pb_percentile_3y = round(len(y3_df[y3_df['pb'] <= eval.pb]) / len(y3_df) * 100, 2)
            item['pb_percentile_3y'] = str(pb_percentile_3y) + '%'
            # 最近 5 年 pe & pb 估值百分位
            y5_start_date = end_date - timedelta(days=365 * 5)
            y5_df = df[df.date >= y5_start_date.strftime('%Y-%m-%d')].copy()
            pe_percentile_5y = round(len(y5_df[y5_df['pe'] <= eval.pe]) / len(y5_df) * 100, 2)
            item['pe_percentile_5y'] = str(pe_percentile_5y) + '%'
            pb_percentile_5y = round(len(y5_df[y5_df['pb'] <= eval.pb]) / len(y5_df) * 100, 2)
            item['pb_percentile_5y'] = str(pb_percentile_5y) + '%'
            # 最近 10 年 pe & pb 估值百分位
            y10_start_date = end_date - timedelta(days=365 * 10)
            y10_df = df[df.date >= y10_start_date.strftime('%Y-%m-%d')].copy()
            pe_percentile_10y = round(len(y10_df[y10_df['pe'] <= eval.pe]) / len(y10_df) * 100, 2)
            item['pe_percentile_10y'] = str(pe_percentile_10y) + '%'
            pb_percentile_10y = round(len(y10_df[y10_df['pb'] <= eval.pb]) / len(y10_df) * 100, 2)
            item['pb_percentile_10y'] = str(pb_percentile_10y) + '%'
            datalist.append(item)
        # [print(x) for x in datalist]
        return {'ultimate': ultimate_values, 'eval': datalist}

    def get_sw_index_current_value(self):
        """
        获取申万 28 行业，以及申万全 A 的指数的实时数据
        """
        # 参考文献 https://www.aibbt.com/a/22051.html
        url = 'http://www.swsindex.com/handler.aspx'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
        # 申万全 A 以及申万 28 行业（前 19 个，到建筑装饰）共计 20个
        param1 = self.__sw_index_form_data('swzs','L1',1,"L1 in('801003', '801002', '801010', '801020', '801030', '801040', '801050', '801080', '801110','801120','801130','801140','801150','801160', '801170', '801180', '801200', '801210', '801230', '801710')",'','L1,L2,L3,L4,L5,L6,L7,L8,L11','20')
        # 申万 28 行业（从电气设备到机械设备）
        param2 = self.__sw_index_form_data('swzs','L1',1,"L1 in('801720', '801730', '801740', '801750', '801760', '801770', '801780', '801790', '801880', '801890')",'','L1,L2,L3,L4,L5,L6,L7,L8,L11','20')
        # 申万风格指数（大盘、中盘、小盘）
        param3 = self.__sw_index_form_data('swzs','L1',1,"L1 in('801811','801812','801813','801821','801822','801823','801831','801832','801833','801841','801842','801843','801851','801852','801853','801861','801862','801863')",'','L1,L2,L3,L4,L5,L6,L7,L8,L11','20')
        
        params = [param1, param2, param3]
        # 并发请求
        requests_list = [grequests.request("POST", url=url, data = x, headers=headers) for x in params]
        response_list = grequests.map(requests_list)
        sw_indexs = []
        sw_styles = []
        # 解析
        for response in response_list:
            if response and response.status_code == 200:
                # L1: "801740"      代码
                # L2: "国防军工     名称
                # L3: "1775.35"     昨收
                # L4: "1774.00"     今开
                # L5: "78889636545.00"  成交额（元）
                # L6: "1870.49"     最高
                # L7: "1744.25"     最低
                # L8: "1744.34"     最新
                # L11: "3543311650" 成交量（股）
                text = response.text.replace('\'','\"').replace('Ａ','A').replace(' ','').replace('指数','')
                datalist = json.loads(text)['root']
                # [print(x) for x in datalist]
                for item in datalist:
                    index = {}
                    index['code'] = item['L1']
                    index['name'] = item['L2']
                    if index['name'] == '申万中小板':
                        index['name'] = '申万中小'
                    index['last_close'] = item['L3']
                    index['open'] = item['L4']
                    index['deal_money'] = item['L5']
                    index['high'] = item['L6']
                    index['low'] = item['L7']
                    index['current'] = item['L8']
                    index['deal_volume'] = item['L11']
                    # 如果请求头包含新股指数，说明是申万风格指数列表，放入申万风格指数结果集，否则放入申万行业指数结果集
                    if u'801863' in response.request.body:
                        sw_styles.append(index)
                    else:
                        sw_indexs.append(index)
        return {'sw_indexs': sw_indexs, 'sw_styles': sw_styles}

    def __sw_index_form_data(self, tablename, key, p, where, ordeby, fieldlist, pagecount, timed=None):
        """
        组织 www.swindex.com 网站 aspx 服务的 post 参数
        """
        values = {'tablename':tablename, 'key':key, 'p':p, 'where':where, 'orderby':ordeby, 'fieldlist':fieldlist, 'pagecount':pagecount, 'timed':time.time()}
        return values

    def get_index_weight(self):
        df = pd.read_csv(os.path.join(self.folder, 'index_weights/all_index_sw_weights.csv'), sep='\t', index_col=[0,1], header=[0,1])
        # 索引
        names = df.index.levels[1]
        indexs = df.index.codes[1]
        # sw1_code
        sw_codes = df.index.levels[0].tolist()
        # sw1_name
        sw_names = []
        # sw1_sequence
        sw_sequences = df.index.codes[0].tolist()
        for i in indexs:
            sw_names.append(names[i])
        # sw1_indexs for DataFrame
        # sw_indexs = list(zip(sw_sequences, sw_codes, sw_names))
        sw_indexs = [{'sequence': x, 'sw1_code': y, 'sw1_name': z} for x, y, z in zip(sw_sequences, sw_codes, sw_names)]
        # print(sw_names, type(sw_names))
        # print(sw_codes, type(sw_codes))
        print(sw_indexs, type(sw_indexs))

        datalist = []
        for x in df.columns:
            index_code = x[0]
            index_name = x[1]
            values = df[index_code, index_name].values.tolist()
            values = [round(x, 3) for x in values]
            datalist.append({'code':index_code.split('.')[0], 'name': index_name, 'weight':values})
            # break
        return {'sw_industry':sw_indexs, 'datalist': datalist}

if __name__ == "__main__":
    sw = swindex()
    sw.get_index_weight()
    #FF6666
    #FF9966
    #FFCC66
    #FFFF66
    #CCFF66
    #99FF66
    #66FF66
    #66FF99
    #66FFCC
    #66FFFF
    #66CCFF
    #6699FF
    #6666FF
    #9966FF
    #CC66FF
    #FF66FF
    #FF66CC
    #FF6699

    pass