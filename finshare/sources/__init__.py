# sources/__init__.py
"""
数据源模块

提供五种数据源实现：
- EastMoneyDataSource: 东方财富（支持历史K线和实时快照）
- TencentDataSource: 腾讯财经（支持历史K线和实时快照）
- SinaDataSource: 新浪财经（仅支持实时快照）
- BaoStockDataSource: BaoStock（支持历史K线）
- TdxDataSource: 通达信（支持历史K线和实时快照）
"""

from finshare.sources.base_source import BaseDataSource
from finshare.sources.eastmoney_source import EastMoneyDataSource
from finshare.sources.tencent_source import TencentDataSource
from finshare.sources.sina_source import SinaDataSource
from finshare.sources.baostock_source import BaoStockDataSource
from finshare.sources.tdx_source import TdxDataSource
from finshare.sources.manager import DataSourceManager

# 单例模式的数据管理器
_manager_instance = None


def get_data_manager():
    """获取数据源管理器（单例）"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = DataSourceManager()
    return _manager_instance


def get_baostock_source():
    """获取 BaoStock 数据源"""
    return BaoStockDataSource()


def get_tdx_source():
    """获取通达信数据源"""
    return TdxDataSource()


__all__ = [
    "BaseDataSource",
    "EastMoneyDataSource",
    "TencentDataSource",
    "SinaDataSource",
    "BaoStockDataSource",
    "TdxDataSource",
    "DataSourceManager",
    "get_data_manager",
    "get_baostock_source",
    "get_tdx_source",
]
