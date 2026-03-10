数据源
=======

支持的 数据源
------------

.. list-table::
   :header-rows: 1

   * - 数据源
     - K线数据
     - 实时快照
     - 复权数据
   * - 东方财富
     - ✅
     - ✅
     - ✅
   * - 腾讯财经
     - ✅
     - ✅
     - ✅
   * - 新浪财经
     - ❌
     - ✅
     - ❌
   * - 通达信
     - ✅
     - ✅
     - ✅
   * - BaoStock
     - ✅
     - ✅
     - ✅

使用特定数据源
--------------

.. code-block:: python

    from finshare import EastMoneyDataSource, TencentDataSource

    # 使用东方财富
    eastmoney = EastMoneyDataSource()
    data = eastmoney.get_historical_data('000001', start='2024-01-01')

    # 使用腾讯财经
    tencent = TencentDataSource()
    data = tencent.get_historical_data('000001', start='2024-01-01')
