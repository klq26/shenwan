# -*- coding: utf-8 -*-
import json

from flask import Flask
from flask import request
from flask import Response
# 跨域
from flask_cors import *

from server.cacheManager import cacheManager
from server.datetimeManager import datetimeManager
from server.swindex import swindex

app = Flask(__name__)
CORS(app, supports_credentials=True)

cm = cacheManager()
dm = datetimeManager()

@app.route('/shenwan/api/index_value', methods=['GET'])
def sw_index_value():
    start_ts = dm.getTimeStamp()
    if cm.cacheAvailable(start_ts, request.path):
        data = cm.getCache(start_ts, request.path)
        return Response(data, status=200, mimetype='application/json')
    # 请求
    sw = swindex()
    results = sw.get_sw_index_current_value()
    end_ts = dm.getTimeStamp()
    duration = dm.getDuration(start_ts, end_ts)
    data = packDataWithCommonInfo(duration = duration, data = results)
    cm.saveCache(request.path, data)
    return Response(data, status=200, mimetype='application/json')

@app.route('/shenwan/api/index_eval', methods=['GET'])
def sw_index_eval():
    start_ts = dm.getTimeStamp()
    if cm.cacheAvailable(start_ts, request.path):
        data = cm.getCache(start_ts, request.path)
        return Response(data, status=200, mimetype='application/json')
    # 请求
    sw = swindex()
    results = sw.get_sw_index_eval()
    end_ts = dm.getTimeStamp()
    duration = dm.getDuration(start_ts, end_ts)
    data = packDataWithCommonInfo(duration = duration, data = results)
    cm.saveCache(request.path, data)
    return Response(data, status=200, mimetype='application/json')

@app.route('/shenwan/api/index_weight', methods=['GET'])
def index_weight():
    start_ts = dm.getTimeStamp()
    if cm.cacheAvailable(start_ts, request.path):
        data = cm.getCache(start_ts, request.path)
        return Response(data, status=200, mimetype='application/json')
    # 请求
    sw = swindex()
    results = sw.get_index_weight()
    end_ts = dm.getTimeStamp()
    duration = dm.getDuration(start_ts, end_ts)
    data = packDataWithCommonInfo(duration = duration, data = results)
    cm.saveCache(request.path, data)
    return Response(data, status=200, mimetype='application/json')

@app.route('/shenwan/api/index_holding', methods=['GET'])
def sw_index_holding():
    start_ts = dm.getTimeStamp()
    if cm.cacheAvailable(start_ts, request.path):
        data = cm.getCache(start_ts, request.path)
        return Response(data, status=200, mimetype='application/json')
    # 请求
    sw = swindex()
    results = sw.get_sw_index_holding()
    end_ts = dm.getTimeStamp()
    duration = dm.getDuration(start_ts, end_ts)
    data = packDataWithCommonInfo(duration = duration, data = results)
    cm.saveCache(request.path, data)
    return Response(data, status=200, mimetype='application/json')

# 添加公共返回值
def packDataWithCommonInfo(isCache = False, isSuccess = True, msg = "success", duration = '0', data = {}):
    code = 0
    if not isSuccess:
        code = -1
    result = {'code' : code, 'msg' : msg, 'isCache' : False, 'aliyun_date' : datetimeManager().getDateTimeString(), 'data' : data, 'duration' : duration}
    return json.dumps(result, ensure_ascii=False, indent=4)

# debug
if __name__ == '__main__':
    app.run(port=5000, debug=True)