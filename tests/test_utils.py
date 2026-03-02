"""
测试 utils 模块

测试工具函数的正确性
"""

import pytest
from finshare.utils import (
    validate_stock_code,
    validate_date,
)


class TestValidateStockCode:
    """测试股票代码验证"""

    def test_valid_sz_code(self):
        """测试有效的深圳股票代码"""
        result, msg = validate_stock_code("000001")
        assert result == True
        result, msg = validate_stock_code("000002")
        assert result == True
        result, msg = validate_stock_code("300001")
        assert result == True

    def test_valid_sh_code(self):
        """测试有效的上海股票代码"""
        result, msg = validate_stock_code("600000")
        assert result == True
        result, msg = validate_stock_code("600036")
        assert result == True
        result, msg = validate_stock_code("601398")
        assert result == True

    def test_invalid_format(self):
        """测试无效格式"""
        result, msg = validate_stock_code("00001")  # 5位
        assert result == False
        result, msg = validate_stock_code("0000001")  # 7位
        assert result == False
        result, msg = validate_stock_code("")
        assert result == False

    def test_invalid_code(self):
        """测试无效代码"""
        result, msg = validate_stock_code("AAPL")
        assert result == False

    def test_edge_cases(self):
        """测试边界情况"""
        result, msg = validate_stock_code(None)
        assert result == False


class TestValidateDate:
    """测试日期验证"""

    def test_valid_date_format(self):
        """测试有效的日期格式"""
        assert validate_date("2024-01-01") == True
        assert validate_date("2024-12-31") == True

    def test_invalid_date_format(self):
        """测试无效的日期格式"""
        assert validate_date("2024/01/01") == False
        assert validate_date("01-01-2024") == False
        # 月份无效
        assert validate_date("2024-13-01") == False

    def test_invalid_date_value(self):
        """测试无效的日期值"""
        assert validate_date("2024-13-01") == False  # 月份无效
        assert validate_date("2024-01-32") == False  # 日期无效

    def test_edge_cases(self):
        """测试边界情况"""
        assert validate_date(None) == False
        assert validate_date("") == False
        assert validate_date("not-a-date") == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
