API 参考
========

核心函数
--------

.. list-table::
   :header-rows: 1

   * - 函数
     - 说明
   * - ``get_historical_data``
     - 获取K线历史数据
   * - ``get_snapshot_data``
     - 获取实时快照
   * - ``get_batch_snapshots``
     - 批量获取快照

财务数据
--------

.. list-table::
   :header-rows: 1

   * - 函数
     - 说明
   * - ``get_income``
     - 利润表
   * - ``get_balance``
     - 资产负债表
   * - ``get_cashflow``
     - 现金流量表
   * - ``get_financial_indicator``
     - 财务指标
   * - ``get_dividend``
     - 分红送转

特色数据
--------

.. list-table::
   :header-rows: 1

   * - 函数
     - 说明
   * - ``get_money_flow``
     - 资金流向
   * - ``get_money_flow_industry``
     - 行业资金流向
   * - ``get_lhb``
     - 龙虎榜
   * - ``get_margin``
     - 融资融券

基金数据
--------

.. list-table::
   :header-rows: 1

   * - 函数
     - 说明
   * - ``get_fund_nav``
     - 基金净值
   * - ``get_fund_info``
     - 基金信息
   * - ``get_fund_list``
     - 基金列表

期货数据
--------

.. list-table::
   :header-rows: 1

   * - 函数
     - 说明
   * - ``get_future_kline``
     - 期货K线
   * - ``get_future_snapshot``
     - 期货快照

证券列表
--------

.. list-table::
   :header-rows: 1

   * - 函数
     - 说明
   * - ``get_stock_list``
     - A股股票列表
   * - ``get_etf_list``
     - ETF列表
   * - ``get_lof_list``
     - LOF列表

高级功能
--------

.. list-table::
   :header-rows: 1

   * - 函数
     - 说明
   * - ``get_async_manager``
     - 异步数据管理器
   * - ``MemoryCache``
     - 内存缓存
   * - ``cached``
     - 缓存装饰器
   * - ``CircuitBreaker``
     - 熔断器
