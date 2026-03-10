"""
证券列表模块

提供股票、ETF、LOF、期货等列表数据获取。
"""

from typing import List, Dict

from finshare.sources.eastmoney_source import EastMoneyDataSource
from finshare.logger import logger

# 创建数据源实例
_list_source = None


def _get_list_source() -> EastMoneyDataSource:
    """获取列表数据源单例"""
    global _list_source
    if _list_source is None:
        _list_source = EastMoneyDataSource()
    return _list_source


def get_stock_list(market: str = "all") -> List[Dict]:
    """
    获取A股股票列表

    Args:
        market: 市场类型
            - "all": 全部股票 (默认)
            - "sh": 上海证券交易所
            - "sz": 深圳证券交易所

    Returns:
        List[Dict] 股票列表，每只股票包含:
        - code: 股票代码
        - name: 股票名称
        - market: 市场代码
        - price: 最新价
        - change_pct: 涨跌幅
        - change: 涨跌额
        - volume: 成交量
        - amount: 成交额

    Examples:
        >>> import finshare as fs
        >>> stocks = fs.get_stock_list()
        >>> print(f"共有 {len(stocks)} 只股票")
        >>> print(stocks[0])
    """
    source = _get_list_source()
    logger.info(f"获取股票列表: market={market}")

    return source.get_stock_list(market)


def get_etf_list() -> List[Dict]:
    """
    获取ETF基金列表

    Returns:
        List[Dict] ETF列表

    Examples:
        >>> import finshare as fs
        >>> etfs = fs.get_etf_list()
        >>> print(f"共有 {len(etfs)} 只ETF")
    """
    source = _get_list_source()
    logger.info("获取ETF列表")

    return source.get_etf_list()


def get_lof_list() -> List[Dict]:
    """
    获取LOF基金列表

    Returns:
        List[Dict] LOF列表

    Examples:
        >>> import finshare as fs
        >>> lofs = fs.get_lof_list()
        >>> print(f"共有 {len(lofs)} 只LOF")
    """
    source = _get_list_source()
    logger.info("获取LOF列表")

    return source.get_lof_list()


def get_future_list() -> List[Dict]:
    """
    获取期货列表

    Returns:
        List[Dict] 期货列表

    Examples:
        >>> import finshare as fs
        >>> futures = fs.get_future_list()
        >>> print(f"共有 {len(futures)} 个期货合约")
    """
    source = _get_list_source()
    logger.info("获取期货列表")

    return source.get_future_list()


__all__ = [
    "get_stock_list",
    "get_etf_list",
    "get_lof_list",
    "get_future_list",
]
