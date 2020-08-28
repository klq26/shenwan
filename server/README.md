* 脚本

swindex.py
    - 和 flask app 对接的总出口。它不直接 import swindex_eval 或 swindex_value 这样的类，而是读取其存放在磁盘上的最新 csv 输出，并做一些 json 化的操作。

swindex_value.py
    - 负责更新申万 28 行业指数的日线历史数据，包括写入本地 csv 文件和云端阿里云数据库。按库存最新日期渐进式更新。

swindex_eval.py
    - 负责更新申万 28 行业指数的日线估值历史数据，包括写入本地 csv 文件和云端阿里云数据库。按库存最新日期渐进式更新。

index_weight.py
    - 负责更新指数的权重数据。

swindex_holding.py
    - 负责把能得到的股票持仓比例和金额，全部转化为申万 28 行业的表达形式。（部分指数基金，部分二级债券公布的前十大持仓股）

swindex_db.py
    - 负责把 eval 估值数据和 price 日线数据写入阿里云数据库，仅做备份之用。

* 数据文件

sw_industry_list.csv
    - 申万 28 行业的代码、名称表。通常用作 DataFrame 的 index 列。

index_weight_list.csv
    - 能获取到权重的列表，可以进行权重到申万 28 行业的转化及分析。

sw_history_daily_price.csv
    - 申万 28 行业历史走势数据。

sw_history_daily_eval.csv
    - 申万 28 行业及全市场历史估值数据。

sw_latest_eval.csv
    - 申万 28 行业及全市场最新一日的数据。

sw_industry_categorys.csv
    - 聚宽全部股票池里，每只股票的申万一二三级分类数据。

index_weights\xx.csv
    - 包含指数的持仓权重、按申万 28 行业 groupby 之后的汇总权重，以及一张把所有指数合并到一起的 DataFrame。
    e.g. 01_000016.XSHG_上证50.csv
        - 带有指数权重和申万一级行业的股票列表。
    e.g. 01_000016.XSHG_上证50_sw.csv
        - 将指数股票列表按申万行业 groupby 后得到的行业权重数据。
    all_index_sw_weights.csv
        - ★ index 是申万 28 行业，column 是每只指数，值是行业权重占比，是一非常重要的表。

sw_holdings\xx.csv
    - 包含指数基金、第三方投资组合中的股票部分，对于申万 28 行业每个行业的真实持仓金额数据。
    category3_holding.csv
        - 按三级分类看，每只指数基金的持仓金额。
    plan365_holding.csv
        - 第三方投资组合股票持仓权重的详细数据。
    sw_index_holding.csv
        - 指数基金中可估算部分对于申万 28 行业每个行业的真实持仓金额数据。
    sw_plan_holding.csv
      - 第三方投资组合中可估算部分对于申万 28 行业每个行业的真实持仓金额数据。
    sw_holding.csv
        - 按申万 28 分类查看每一个行业的持仓金额（包含了指数基金单列、组合单列、汇总数据等）。