快速开始
==========

基础用法
--------

.. code-block:: python

    import finshare as fs

    # 获取历史K线数据
    df = fs.get_historical_data('000001.SZ', start='2024-01-01', end='2024-01-31')
    print(df.head())

    # 获取实时快照
    snapshot = fs.get_snapshot_data('000001.SZ')
    print(f"最新价: {snapshot.last_price}")

股票代码格式
------------

finshare 支持多种股票代码格式：

.. code-block:: python

    # 以下格式均可使用
    '000001.SZ'   # 标准格式
    '000001'      # 纯数字（自动识别市场）
    'SZ000001'    # SZ前缀

支持的交易市场：

.. list-table::
   :header-rows: 1

   * - 市场
     - 代码后缀
     - 示例
   * - 深圳
     - .SZ
     - 000001.SZ
   * - 上海
     - .SH
     - 600519.SH
   * - 北京
     - .BJ
     - 430001.BJ
   * - 港股
     - .HK
     - 00700.HK
   * - 美股
     - .US
     - AAPL.US
