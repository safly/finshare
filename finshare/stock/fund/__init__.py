"""
基金数据模块

提供基金净值、基金信息等数据获取。
"""

from typing import List, Optional, Dict
from datetime import date, datetime, timedelta

from finshare.sources.fund_source import FundDataSource
from finshare.models.data_models import FundData
from finshare.logger import logger

# 创建基金数据源实例
_fund_source = None


def _get_fund_source() -> FundDataSource:
    """获取基金数据源单例"""
    global _fund_source
    if _fund_source is None:
        _fund_source = FundDataSource()
    return _fund_source


def get_fund_nav(
    code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[FundData]:
    """
    获取基金净值数据

    Args:
        code: 基金代码 (如 161039, 000001)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        List[FundData] 基金净值数据列表

    Examples:
        >>> import finshare as fs
        >>> data = fs.get_fund_nav('161039', '2024-01-01', '2024-01-31')
        >>> for item in data:
        >>>     print(f"{item.nav_date}: nav={item.nav}, change_pct={item.change_pct}%")
    """
    source = _get_fund_source()

    # 解析日期
    if start_date:
        start = _parse_date(start_date)
    else:
        start = date.today() - timedelta(days=90)

    if end_date:
        end = _parse_date(end_date)
    else:
        end = date.today()

    logger.info(f"获取基金净值: {code}, {start} - {end}")

    return source.get_fund_nav(code, start, end)


def get_fund_info(code: str) -> Optional[dict]:
    """
    获取基金基本信息

    Args:
        code: 基金代码

    Returns:
        基金信息字典，包含基金规模、经理等信息

    Examples:
        >>> import finshare as fs
        >>> info = fs.get_fund_info('161039')
        >>> print(info)
    """
    source = _get_fund_source()
    logger.debug(f"获取基金信息: {code}")

    return source.get_fund_info(code)


def get_fund_list(market: str = "all") -> List[dict]:
    """
    获取基金列表

    Args:
        market: 市场类型 (all: 全部, sh: 上海, sz: 深圳)

    Returns:
        基金列表

    Examples:
        >>> import finshare as fs
        >>> funds = fs.get_fund_list()
        >>> print(f"共有 {len(funds)} 只基金")
    """
    source = _get_fund_source()
    logger.debug(f"获取基金列表: market={market}")

    return source.get_fund_list(market)


def _parse_date(date_str: str) -> date:
    """解析日期字符串"""
    if isinstance(date_str, date):
        return date_str

    date_str = str(date_str).replace("-", "").replace("/", "")

    if len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d").date()

    return date.today()


__all__ = [
    "get_fund_nav",
    "get_fund_info",
    "get_fund_list",
]
