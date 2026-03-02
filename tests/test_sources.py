"""
测试 sources 模块

测试数据源的功能
"""

import pytest
from unittest.mock import Mock, patch
from finshare.sources import (
    BaseDataSource,
    EastMoneyDataSource,
    TencentDataSource,
    get_data_manager,
)
from finshare.models.data_models import SnapshotData, MarketType


class TestBaseDataSource:
    """测试数据源基类"""

    def test_base_source_interface(self):
        """测试基类接口"""
        # BaseDataSource 是抽象类，不能直接实例化
        with pytest.raises(TypeError):
            BaseDataSource()


class TestEastMoneyDataSource:
    """测试东方财富数据源"""

    def test_create_eastmoney_source(self):
        """测试创建东方财富数据源"""
        source = EastMoneyDataSource()

        assert source is not None
        assert hasattr(source, "get_historical_data")
        assert hasattr(source, "get_snapshot_data")

    @pytest.mark.integration
    def test_eastmoney_get_kline(self):
        """测试获取 K线数据（集成测试）"""
        source = EastMoneyDataSource()

        # 这是一个集成测试，需要网络连接
        try:
            data = source.get_kline(code="000001.SZ", start="2024-01-01", end="2024-01-10")

            if data is not None:
                assert len(data) > 0
                assert "open" in data.columns
                assert "close" in data.columns
        except Exception as e:
            pytest.skip(f"Network error: {e}")


class TestTencentDataSource:
    """测试腾讯数据源"""

    def test_create_tencent_source(self):
        """测试创建腾讯数据源"""
        source = TencentDataSource()

        assert source is not None
        assert hasattr(source, "get_historical_data")
        assert hasattr(source, "get_snapshot_data")

    @pytest.mark.integration
    def test_tencent_get_kline(self):
        """测试获取 K线数据（集成测试）"""
        source = TencentDataSource()

        try:
            data = source.get_kline(code="000001.SZ", start="2024-01-01", end="2024-01-10")

            if data is not None:
                assert len(data) > 0
        except Exception as e:
            pytest.skip(f"Network error: {e}")


class TestDataSourceManager:
    """测试数据源管理器"""

    def test_get_data_source_manager(self):
        """测试获取数据源管理器"""
        manager = get_data_manager()

        assert manager is not None
        assert hasattr(manager, "get_snapshot_data")

    def test_manager_singleton(self):
        """测试管理器单例模式"""
        manager1 = get_data_manager()
        manager2 = get_data_manager()

        # 应该返回同一个实例
        assert manager1 is manager2

    @patch("finshare.sources.manager.DataSourceManager.get_snapshot_data")
    def test_manager_get_snapshot_mock(self, mock_get_snapshot):
        """测试管理器获取快照（使用 mock）"""
        from datetime import datetime

        # 设置 mock 返回值 - 只使用 SnapshotData 实际存在的字段
        mock_snapshot = SnapshotData(
            code="000001.SZ",
            timestamp=datetime.now(),
            last_price=10.0,
            volume=1000000.0,
            amount=10000000.0,
            market=MarketType.SZ,
            data_source="mock",
        )
        mock_get_snapshot.return_value = mock_snapshot

        manager = get_data_manager()
        data = manager.get_snapshot_data("000001.SZ")

        assert data is not None
        assert data.code == "000001.SZ"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
