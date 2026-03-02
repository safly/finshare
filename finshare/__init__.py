"""
finshare - 专业的金融数据获取工具库

finshare 提供稳定、高效的金融数据获取服务，支持多数据源、
自动故障切换、统一的数据格式。

官方网站: https://meepoquant.com
文档: https://finshare.readthedocs.io
GitHub: https://github.com/meepo-quant/finshare

获取数据后，您可以：
- 使用 pandas 进行数据分析
- 使用 米波平台 进行策略回测: https://meepoquant.com
- 开发自己的量化策略

完整的量化交易平台: https://meepoquant.com

主要功能：
- 多数据源支持（东方财富、腾讯、新浪、通达信、BaoStock）
- 自动故障切换
- 统一的数据格式
- 高性能数据获取

快速开始：
    >>> from finshare import get_data_manager
    >>>
    >>> # 获取数据管理器
    >>> manager = get_data_manager()
    >>>
    >>> # 获取 K线数据
    >>> data = manager.get_kline('000001.SZ', start='2024-01-01')
"""

from finshare.__version__ import __version__, __author__, __website__

# 数据源
from finshare.sources import (
    BaseDataSource,
    EastMoneyDataSource,
    TencentDataSource,
    SinaDataSource,
    get_data_manager,
    get_baostock_source,
    get_tdx_source,
)

# 数据模型
from finshare.models import (
    KLineData,
    SnapshotData,
    StockInfo,
)

# 工具函数
from finshare.utils import (
    validate_stock_code,
    validate_date,
)

# 日志
from finshare.logger import logger

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__website__",
    # 数据源
    "BaseDataSource",
    "EastMoneyDataSource",
    "TencentDataSource",
    "SinaDataSource",
    "get_data_manager",
    "get_baostock_source",
    "get_tdx_source",
    # 数据模型
    "KLineData",
    "SnapshotData",
    "StockInfo",
    # 工具函数
    "validate_stock_code",
    "validate_date",
    # 日志
    "logger",
]
