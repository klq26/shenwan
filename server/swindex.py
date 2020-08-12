# -*- coding: utf-8 -*-

import os
import sys
import json
import time
from datetime import datetime

import grequests
import pandas as pd

class swindex:
    """
    获取和申万 28 行业有关的数据（指数走势、指数等权估值及百分位等）
    """
    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.eval_folder = os.path.join(self.folder, u'申万行业估值')
        self.all_market_eval_name = u'全市场整体'
        pass

    def get_sw_index_eval(self, name, csv_path):
        """
        获取申万 28 行业，以及申万全 A 的指数估值
        """
        # 读取全市场数据
        df = pd.read_csv(csv_path, sep='\t', index_col=0)
        pe = df.iloc[-1].pe
        pe_percentile = round(len(df[df['pe'] <= df.iloc[-1].pe]) / len(df) * 100, 2)

        pb = df.iloc[-1].pb
        count = 0
        if 'total_count' in list(df.iloc[-1].index):
            count = df.iloc[-1].total_count
        pb_percentile = round(len(df[df['pb'] <= df.iloc[-1].pb]) / len(df) * 100, 2)
        return {'name': name,'count':count, 'pe': pe, 'pe_percentile':str(pe_percentile) + '%', 'pb':pb, 'pb_percentile': str(pb_percentile) + '%'}

    def get_sw_index_value(self):
        """
        获取申万 28 行业，以及申万全 A 的指数点位
        """
        # 参考文献 https://www.aibbt.com/a/22051.html
        url = 'http://www.swsindex.com/handler.aspx'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
        # 申万全 A 以及申万 28 行业（前 19 个，到建筑装饰）共计 20个
        param1 = self.sw_index_form_data('swzs','L1',1,"L1 in('801003', '801002', '801010', '801020', '801030', '801040', '801050', '801080', '801110','801120','801130','801140','801150','801160', '801170', '801180', '801200', '801210', '801230', '801710')",'','L1,L2,L3,L4,L5,L6,L7,L8,L11','20')
        # 申万 28 行业（从电气设备到机械设备）
        param2 = self.sw_index_form_data('swzs','L1',1,"L1 in('801720', '801730', '801740', '801750', '801760', '801770', '801780', '801790', '801880', '801890')",'','L1,L2,L3,L4,L5,L6,L7,L8,L11','20')
        # 申万风格指数（大盘、中盘、小盘）
        param3 = self.sw_index_form_data('swzs','L1',1,"L1 in('801811','801812','801813','801821','801822','801823','801831','801832','801833','801841','801842','801843','801851','801852','801853','801861','801862','801863')",'','L1,L2,L3,L4,L5,L6,L7,L8,L11','20')
        
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

    def sw_index_form_data(self, tablename, key, p, where, ordeby, fieldlist, pagecount, timed=None):
        """
        组织 www.swindex.com 网站 aspx 服务的 post 参数
        """
        values = {'tablename':tablename, 'key':key, 'p':p, 'where':where, 'orderby':ordeby, 'fieldlist':fieldlist, 'pagecount':pagecount, 'timed':time.time()}
        return values

if __name__ == "__main__":
    sw = swindex()
    datalist = sw.get_sw_index_value()
    print(datalist)
    # results = []
    # for root, dirs, files in os.walk(sw.eval_folder):
    #     for f in files:
    #         # print(os.path.join(root, f))
    #         results.append(sw.get_sw_index_eval(name = f.replace('.csv',''), csv_path = os.path.join(root, f)))
    # [print('{0}\t{1}\t{2}\t{3}'.format(x['name'],x['count'], x['pe_percentile'], x['pb_percentile'])) for x in results]
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