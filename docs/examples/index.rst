示例代码
========

基础示例
--------

.. code-block:: python

    import finshare as fs

    # 获取日线数据
    df = fs.get_historical_data(
        code='000001.SZ',
        start='2024-01-01',
        end='2024-01-31',
        adjust='qfq'
    )

    # 获取实时快照
    snapshot = fs.get_snapshot_data('000001.SZ')
    print(f"最新价: {snapshot.last_price}")

批量获取
--------

.. code-block:: python

    import finshare as fs

    codes = ['000001.SZ', '600519.SH', '510300']

    # 批量获取快照
    results = fs.get_batch_snapshots(codes)

    for code, snapshot in results.items():
        print(f"{code}: {snapshot.last_price}")

基金数据
--------

.. code-block:: python

    import finshare as fs

    # 获取基金净值
    fund_data = fs.get_fund_nav('161039', '2024-01-01', '2024-12-31')

    for item in fund_data:
        print(f"{item.nav_date}: nav={item.nav}")

期货数据
--------

.. code-block:: python

    import finshare as fs

    # 获取期货K线
    future_data = fs.get_future_kline('cu0', '2024-06-01', '2024-07-17')

    print(f"共 {len(future_data)} 条数据")
