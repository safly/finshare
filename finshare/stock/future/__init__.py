"""
期货数据模块

提供期货历史K线和实时行情数据获取。
"""

from typing import List, Optional, Dict
from datetime import date

from finshare.sources.future_source import FutureDataSource
from finshare.models.data_models import HistoricalData, FutureSnapshotData, FutureExchange, AdjustmentType
from finshare.logger import logger

# 创建期货数据源实例
_future_source = None


def _get_future_source() -> FutureDataSource:
    """获取期货数据源单例"""
    global _future_source
    if _future_source is None:
        _future_source = FutureDataSource()
    return _future_source


def get_future_kline(
    code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    adjustment: AdjustmentType = AdjustmentType.NONE,
) -> List[HistoricalData]:
    """
    获取期货历史K线数据

    Args:
        code: 期货合约代码 (如 IF2409, CU2409, RB2409)
              也支持简写: IF0 (沪深300股指当月连续), CU0 (沪铜当月连续)
        start_date: 开始日期 (YYYY-MM-DD 或 YYYYMMDD)
        end_date: 结束日期 (YYYY-MM-DD 或 YYYYMMDD)
        adjustment: 复权类型 (期货不支持，默认为NONE)

    Returns:
        List[HistoricalData] 历史K线数据列表

    Examples:
        >>> import finshare as fs
        >>> data = fs.get_future_kline('IF2409', '2024-01-01', '2024-01-31')
        >>> print(data)
    """
    source = _get_future_source()

    # 解析日期
    if start_date:
        start_date = _parse_date(start_date)
    else:
        start_date = date.today() - timedelta(days=30)

    if end_date:
        end_date = _parse_date(end_date)
    else:
        end_date = date.today()

    logger.info(f"获取期货K线: {code}, {start_date} - {end_date}")

    return source.get_historical_data(code, start_date, end_date, adjustment)


def get_future_snapshot(code: str) -> Optional[FutureSnapshotData]:
    """
    获取期货实时快照数据

    Args:
        code: 期货合约代码 (如 IF2409, CU2409)

    Returns:
        FutureSnapshotData 实时快照数据

    Examples:
        >>> import finshare as fs
        >>> snapshot = fs.get_future_snapshot('IF2409')
        >>> print(f"最新价: {snapshot.last_price}, 持仓: {snapshot.open_interest}")
    """
    source = _get_future_source()
    logger.debug(f"获取期货快照: {code}")

    return source.get_future_snapshot(code)


def get_batch_future_snapshots(codes: List[str]) -> Dict[str, FutureSnapshotData]:
    """
    批量获取期货实时快照

    Args:
        codes: 期货合约代码列表

    Returns:
        Dict[str, FutureSnapshotData] 代码 -> 快照数据

    Examples:
        >>> import finshare as fs
        >>> snapshots = fs.get_batch_future_snapshots(['IF2409', 'CU2409', 'AU2409'])
    """
    source = _get_future_source()
    logger.debug(f"批量获取期货快照: {len(codes)} 只")

    return source.get_batch_future_snapshots(codes)


def _parse_date(date_str: str) -> date:
    """解析日期字符串"""
    if isinstance(date_str, date):
        return date_str

    date_str = str(date_str).replace("-", "").replace("/", "")

    if len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d").date()

    return date.today()


from datetime import datetime, timedelta  # noqa: E402


__all__ = [
    "get_future_kline",
    "get_future_snapshot",
    "get_batch_future_snapshots",
]
