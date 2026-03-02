"""
测试 models 模块

测试数据模型的创建和验证
"""

import pytest
from datetime import datetime, date
from finshare.models import (
    HistoricalData,
    SnapshotData,
)


class TestHistoricalData:
    """测试 HistoricalData 类"""

    def test_create_kline(self):
        """测试创建 K线数据"""
        kline = HistoricalData(
            code="000001",
            trade_date=date.today(),
            open_price=10.00,
            high_price=10.50,
            low_price=9.80,
            close_price=10.30,
            volume=1000000,
            amount=10500000,
        )

        assert kline.code == "000001"
        assert kline.open_price == 10.00
        assert kline.high_price == 10.50
        assert kline.low_price == 9.80
        assert kline.close_price == 10.30

    def test_kline_validation(self):
        """测试 K线数据验证"""
        # 正常情况：high >= low
        kline = HistoricalData(
            code="000001",
            trade_date=date.today(),
            open_price=10.00,
            high_price=10.50,
            low_price=9.80,
            close_price=10.30,
            volume=1000000,
            amount=10500000,
        )

        assert kline.high_price >= kline.low_price
        assert kline.high_price >= kline.open_price
        assert kline.high_price >= kline.close_price
        assert kline.low_price <= kline.open_price
        assert kline.low_price <= kline.close_price


class TestSnapshotData:
    """测试 SnapshotData 类"""

    def test_create_snapshot(self, mock_snapshot_data):
        """测试创建快照数据"""
        snapshot = SnapshotData(**mock_snapshot_data)

        assert snapshot.code == "000001.SZ"
        assert snapshot.last_price == 10.50

    def test_snapshot_volume(self, mock_snapshot_data):
        """测试快照成交量"""
        snapshot = SnapshotData(**mock_snapshot_data)

        assert snapshot.volume == 1000000
        assert snapshot.amount == 10500000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
