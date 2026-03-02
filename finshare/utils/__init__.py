"""
finshare Utils Module

工具函数模块，提供数据验证等辅助功能。

主要函数：
- validate_stock_code: 验证股票代码
"""

from finshare.utils.validators import (
    validate_stock_code,
)


# 添加简单的 validate_date 和 validate_price 函数
def validate_date(date_str):
    """验证日期格式"""
    if not date_str or not isinstance(date_str, str):
        return False
    try:
        from datetime import datetime

        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False


def validate_price(price):
    """验证价格"""
    if price is None:
        return False
    try:
        return float(price) > 0
    except:
        return False


__all__ = [
    "validate_stock_code",
    "validate_date",
    "validate_price",
]
