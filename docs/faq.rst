常见问题
========

Q: 需要 API Key 吗？
-------------------

A: 不需要，finshare 完全免费使用。

Q: 有调用次数限制吗？
-------------------

A: 没有硬性限制，但建议合理使用，设置适当的请求间隔。

Q: 数据从哪里获取？
-----------------

A: finshare 从多个公开数据源获取（东方财富、腾讯、新浪等），不存储数据。

Q: 支持哪些 Python 版本？
----------------------

A: 支持 Python 3.8 及以上版本。

Q: 如何获取港股数据？
------------------

A: 使用港股代码格式，如 ``00700.HK``、``09988.HK``。

.. code-block:: python

    import finshare as fs

    # 获取港股快照
    snapshot = fs.get_snapshot_data('00700.HK')
    print(f"腾讯控股: {snapshot.last_price} 港元")

Q: 如何获取期货数据？
------------------

A: 使用期货代码，如 ``cu0``（沪铜连续）、``IF0``（沪深300股指）。

.. code-block:: python

    import finshare as fs

    # 获取期货K线
    data = fs.get_future_kline('cu0', '2024-01-01', '2024-12-31')
