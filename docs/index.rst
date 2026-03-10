.. finshare documentation master file

finshare | 专业的金融数据获取工具库
=============================================

.. image:: https://img.shields.io/github/stars/finvfamily/finshare
   :target: https://github.com/finvfamily/finshare
   :alt: GitHub stars

.. image:: https://img.shields.io/pypi/v/finshare
   :target: https://pypi.org/project/finshare/
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/finshare
   :target: https://pypi.org/project/finshare/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/finvfamily/finshare
   :target: https://github.com/finvfamily/finshare/blob/main/LICENSE
   :alt: License

finshare 是一个专业的金融数据获取 Python 库，支持从多个数据源获取股票、ETF、LOF、期货等金融产品的历史数据、实时行情、财务数据、特色数据等。

**完全免费**：无需 API Key，无调用次数限制

.. toctree::
   :maxdepth: 2
   :caption: 文档目录

   install
   quickstart
   data_source
   api/index
   examples/index
   faq

功能特性
--------

- **多数据源支持** - 东方财富、腾讯、新浪、通达信、BaoStock
- **自动故障切换** - 数据源失败时自动切换备用源
- **高性能获取** - 支持异步批量获取
- **内置缓存机制** - 减少重复请求
- **简单易用的 API 设计** - 开箱即用

快速开始
--------

安装::

    pip install finshare

使用::

    import finshare as fs

    # 获取历史K线数据
    df = fs.get_historical_data('000001.SZ', start='2024-01-01', end='2024-01-31')
    print(df.head())

    # 获取实时快照
    snapshot = fs.get_snapshot_data('000001.SZ')
    print(f"最新价: {snapshot.last_price}")

支持的数据类型
-------------

.. list-table::
   :header-rows: 1

   * - 数据类型
     - 接口函数
     - 说明
   * - 股票K线
     - ``get_historical_data``
     - 日线、周线、月线
   * - 实时快照
     - ``get_snapshot_data``
     - 实时行情
   * - 基金净值
     - ``get_fund_nav``
     - 场外基金净值
   * - 期货K线
     - ``get_future_kline``
     - 期货历史数据
   * - 证券列表
     - ``get_stock_list``
     - A股、ETF、LOF列表

.. note::

   本项目完全由 AI (Claude) 实现，展示了 AI 在软件工程领域的强大能力。

.. include:: ../README.md
   :parser: myst_parser.sphinx_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
