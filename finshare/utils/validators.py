import re
from datetime import datetime, date
from typing import Optional, Tuple


def validate_stock_code(code: str) -> Tuple[bool, str]:
    """
    验证股票代码格式

    Args:
        code: 股票代码

    Returns:
        (是否有效, 错误信息)
    """
    if not code:
        return False, "股票代码不能为空"

    # 移除可能的前缀
    clean_code = re.sub(r"^(SH|SZ|BJ|sh|sz|bj)", "", code.upper())

    # 验证长度
    if len(clean_code) != 6:
        return False, f"股票代码长度应为6位，当前为{len(clean_code)}位"

    # 验证是否为数字
    if not clean_code.isdigit():
        return False, "股票代码应全为数字"

    # 验证市场代码
    if code.upper().startswith("SH") or code.startswith("6"):
        if not clean_code.startswith(("6", "5")):
            return False, "沪市股票代码应以6或5开头"
    elif code.upper().startswith("SZ") or code.startswith(("0", "3")):
        if not clean_code.startswith(("0", "3")):
            return False, "深市股票代码应以0或3开头"
    elif code.upper().startswith("BJ") or code.startswith("9"):
        if not clean_code.startswith("9"):
            return False, "北交所股票代码应以4或8开头"

    return True, ""


def validate_date_range(start_date: date, end_date: date) -> Tuple[bool, str]:
    """
    验证日期范围

    Args:
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        (是否有效, 错误信息)
    """
    if not start_date or not end_date:
        return False, "开始日期和结束日期不能为空"

    if start_date > end_date:
        return False, "开始日期不能晚于结束日期"

    if end_date > date.today():
        return False, "结束日期不能晚于今天"

    # 检查日期范围是否过大
    delta = (end_date - start_date).days
    if delta > 365 * 10:  # 限制10年
        return False, "日期范围不能超过10年"

    return True, ""


def validate_price_data(
    open_price: float, high_price: float, low_price: float, close_price: float
) -> Tuple[bool, str]:
    """
    验证价格数据的合理性

    Args:
        open_price: 开盘价
        high_price: 最高价
        low_price: 最低价
        close_price: 收盘价

    Returns:
        (是否有效, 错误信息)
    """
    # 检查价格是否为正数
    if any(price < 0 for price in [open_price, high_price, low_price, close_price]):
        return False, "价格不能为负数"

    # 检查价格合理性
    if high_price < low_price:
        return False, "最高价不能低于最低价"

    if open_price > high_price or open_price < low_price:
        return False, "开盘价应在最高价和最低价之间"

    if close_price > high_price or close_price < low_price:
        return False, "收盘价应在最高价和最低价之间"

    return True, ""


def validate_volume_data(volume: float, amount: float, price: float) -> Tuple[bool, str]:
    """
    验证成交量和成交额数据的合理性

    Args:
        volume: 成交量
        amount: 成交额
        price: 价格

    Returns:
        (是否有效, 错误信息)
    """
    if volume < 0:
        return False, "成交量不能为负数"

    if amount < 0:
        return False, "成交额不能为负数"

    # 检查成交额与成交量的关系（近似检查）
    if volume > 0 and price > 0:
        expected_amount = volume * price
        if amount > 0 and abs(expected_amount - amount) / expected_amount > 0.5:
            return False, f"成交额与成交量*价格不匹配: 期望{expected_amount:.2f}, 实际{amount:.2f}"

    return True, ""


def normalize_stock_code(code: str) -> str:
    """
    标准化股票代码格式

    Args:
        code: 原始股票代码

    Returns:
        标准化后的股票代码
    """
    # 移除空格和特殊字符
    clean_code = re.sub(r"[^\w]", "", code.upper())

    # 如果已经有市场前缀，保持原样
    if clean_code.startswith(("SH", "SZ", "BJ")):
        return clean_code

    # 根据代码添加市场前缀
    if clean_code.startswith(("6", "5")):
        return f"SH{clean_code}"
    elif clean_code.startswith(("0", "1", "3")):
        return f"SZ{clean_code}"
    elif clean_code.startswith("9"):
        return f"BJ{clean_code}"
    else:
        return clean_code
