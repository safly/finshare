"""
pytest 配置文件

提供测试夹具和共享配置
"""

import pytest
import pandas as pd
from datetime import datetime


@pytest.fixture
def sample_kline_data():
    """
    生成示例 K线数据

    Returns:
        DataFrame: 包含 OHLCV 数据的 DataFrame
    """
    dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
    data = pd.DataFrame(
        {
            "open": 10.0 + pd.Series(range(20)) * 0.1,
            "high": 10.5 + pd.Series(range(20)) * 0.1,
            "low": 9.5 + pd.Series(range(20)) * 0.1,
            "close": 10.0 + pd.Series(range(20)) * 0.1,
            "volume": 1000000,
        },
        index=dates,
    )
    return data


@pytest.fixture
def sample_stock_codes():
    """
    生成示例股票代码列表

    Returns:
        list: 股票代码列表
    """
    return [
        "000001.SZ",  # 平安银行
        "000002.SZ",  # 万科A
        "600000.SH",  # 浦发银行
        "600036.SH",  # 招商银行
    ]


@pytest.fixture
def mock_snapshot_data():
    """
    生成模拟快照数据

    Returns:
        dict: 快照数据字典
    """
    return {
        "code": "000001.SZ",
        "last_price": 10.50,
        "volume": 1000000,
        "amount": 10500000,
        "timestamp": datetime.now(),
    }


# 测试标记
def pytest_configure(config):
    """配置自定义测试标记"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (need network)"
    )
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
