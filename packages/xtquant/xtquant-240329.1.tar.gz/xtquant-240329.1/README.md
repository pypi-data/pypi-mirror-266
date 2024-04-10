## 数据
郑商所期货品种支持使用4位年月代码（例如：CF2303.ZF）

xtdata.get_instrument_detail()支持使用4位年月代码获取

历史主力合约数据 新增4位年月代码字段

支持获取etf的iopv数据
分笔数据添加iopv字段（pe）
xtdata.get_market_data()系列函数 数据周期：etfiopv1m（分钟级） etfiopv1d（日级）

期权函数xtdata.get_option_detail_data() 新增标的品种代码字段 OptUndlCodeFull

新增板块 上证转债、沪深转债、T+0基金

## 功能
连接状态监听接口回调数据结构调整
xtdata.watch_quote_server_status()
xtdata.watch_xtquant_status()

新增接口 xtdata.subscribe_formula() 支持连接投研端调用vba

token模式下支持按用户权限放开并行接入数量

本地python回测支持多线程

优化7*24连续交易的问题