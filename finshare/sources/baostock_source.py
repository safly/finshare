# sources/baostock_source.py
"""
BaoStock 数据源实现

功能：历史K线数据获取（支持前复权）
特点：免费、无需注册、数据稳定
限制：实时行情更新较慢（日K需等收盘后）

官方文档：http://baostock.com/baostock/index.php/Python_API文档
"""

from datetime import date, datetime
from typing import List, Optional, Dict
import baostock as bs
from finshare.models.data_models import HistoricalData, SnapshotData, AdjustmentType, MarketType
from finshare.logger import logger
from finshare.sources.base_source import BaseDataSource


class BaoStockDataSource(BaseDataSource):
    """
    BaoStock 数据源实现

    主要用途：获取历史K线数据（支持前复权）
    不推荐用途：实时行情（更新较慢）

    注意：BaoStock 对 ETF/LOF 的历史数据支持有限，
    建议 ETF/LOF 优先使用腾讯或东方财富数据源。
    """

    # 类级别的登录状态（所有实例共享）
    _is_logged_in = False
    _login_lock = None

    def __init__(self):
        super().__init__("baostock")
        self._initialized = False
        # 初始化类级别的锁（只初始化一次）
        if BaoStockDataSource._login_lock is None:
            import threading

            BaoStockDataSource._login_lock = threading.Lock()

    def _ensure_login(self) -> bool:
        """确保已登录 BaoStock（线程安全）"""
        if BaoStockDataSource._is_logged_in:
            return True

        with BaoStockDataSource._login_lock:
            # 双重检查锁定
            if BaoStockDataSource._is_logged_in:
                return True

            try:
                lg = bs.login()
                if lg.error_code == "0":
                    BaoStockDataSource._is_logged_in = True
                    logger.info("BaoStock 登录成功")
                    return True
                else:
                    logger.warning(f"BaoStock 登录失败: {lg.error_msg}")
                    return False
            except Exception as e:
                logger.error(f"BaoStock 登录异常: {e}")
                return False

    def get_historical_data(
        self,
        code: str,
        start_date: date,
        end_date: date,
        adjustment: AdjustmentType = AdjustmentType.NONE,
    ) -> List[HistoricalData]:
        """
        获取历史K线数据

        Args:
            code: 股票代码（如 600519 或 SH600519）
            start_date: 开始日期
            end_date: 结束日期
            adjustment: 复权类型（NONE/PREVIOUS/POST）

        Returns:
            历史数据列表
        """

        # 检查冷却状态
        if self.is_in_cooldown():
            remaining = self.get_cooldown_remaining()
            logger.debug(f"BaoStock 在冷却中，剩余 {remaining/3600:.1f}小时")
            return []

        # 确保已登录
        if not self._ensure_login():
            self._enter_cooldown("登录失败")
            return []

        try:
            # 转换代码格式
            bs_code = self._convert_to_bs_code(code)
            full_code = self._ensure_full_code(code)

            # 转换复权类型
            adjust_flag = self._convert_adjustment_type(adjustment)

            # 请求频率限制
            self._rate_limit()

            # 查询历史K线
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,code,open,high,low,close,volume,amount,adjustflag,turn",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                frequency="d",
                adjustflag=adjust_flag,
            )

            if rs.error_code != "0":
                logger.warning(f"BaoStock 查询失败: {rs.error_msg}")
                self._enter_cooldown(f"查询失败: {rs.error_msg}")
                return []

            # 解析数据
            historical_list = []
            while rs.next():
                row = rs.get_row_data()
                try:
                    hist_data = self._parse_row(row, full_code, adjustment)
                    if hist_data:
                        historical_list.append(hist_data)
                except Exception as e:
                    logger.debug(f"解析数据行失败: {e}")
                    continue

            logger.info(f"[BaoStock] 获取历史数据成功: {full_code}, 共{len(historical_list)}条")
            return historical_list

        except Exception as e:
            logger.error(f"BaoStock 获取历史数据失败 {code}: {e}")
            self._enter_cooldown(f"请求异常: {e}")
            return []

    def _parse_row(
        self, row: List[str], code: str, adjustment: AdjustmentType
    ) -> Optional[HistoricalData]:
        """解析单行数据"""
        # row: [date, code, open, high, low, close, volume, amount, adjustflag, turn]
        if len(row) < 8:
            return None

        trade_date_str, _, open_p, high_p, low_p, close_p, volume, amount = row[:8]
        turn = row[9] if len(row) > 9 else None

        # 跳过空数据
        if not open_p or not close_p:
            return None

        return HistoricalData(
            code=code,
            trade_date=datetime.strptime(trade_date_str, "%Y-%m-%d").date(),
            open_price=float(open_p),
            high_price=float(high_p),
            low_price=float(low_p),
            close_price=float(close_p),
            volume=float(volume) / 100 if volume else 0,  # BaoStock返回股数，转换为手
            amount=float(amount) if amount else 0,
            turnover_rate=float(turn) if turn else None,
            adjust_factor=1.0,
            market=self._get_market_type(code),
            adjustment=adjustment,
            data_source=self.source_name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def get_snapshot_data(self, code: str) -> Optional[SnapshotData]:
        """
        获取实时快照数据

        注意：BaoStock 不支持实时行情数据，请使用其他数据源
        推荐使用 TDX、东方财富或腾讯获取实时数据
        """
        raise NotImplementedError(
            "BaoStock 不支持实时行情数据，请使用 TdxDataSource、EastMoneyDataSource 或 TencentDataSource"
        )

    def get_batch_snapshots(self, codes: List[str]) -> Dict[str, SnapshotData]:
        """
        批量获取快照数据

        注意：BaoStock 不支持实时行情数据，请使用其他数据源
        """
        raise NotImplementedError(
            "BaoStock 不支持实时行情数据，请使用 TdxDataSource、EastMoneyDataSource 或 TencentDataSource"
        )

    def get_batch_snapshots_fallback(self, codes: List[str]) -> Dict[str, SnapshotData]:
        """保留原方法用于向后兼容，但返回空结果"""
        results = {}
        for code in codes:
            snapshot = self.get_snapshot_data(code)
            if snapshot:
                results[self._ensure_full_code(code)] = snapshot
        return results

    def _convert_to_bs_code(self, code: str) -> str:
        """
        转换为 BaoStock 代码格式

        BaoStock 格式: sh.600519 或 sz.000001
        """
        full_code = self._ensure_full_code(code)

        if full_code.startswith("SH"):
            return f"sh.{full_code[2:]}"
        elif full_code.startswith("SZ"):
            return f"sz.{full_code[2:]}"
        elif full_code.startswith("BJ"):
            return f"bj.{full_code[2:]}"
        else:
            # 根据数字判断
            clean_code = full_code.replace("SH", "").replace("SZ", "").replace("BJ", "")
            if clean_code and clean_code[0].isdigit():
                first_digit = clean_code[0]
                if first_digit in ["6", "5"]:
                    return f"sh.{clean_code}"
                elif first_digit in ["0", "1", "2", "3"]:
                    return f"sz.{clean_code}"
            return f"sh.{clean_code}"

    def _convert_adjustment_type(self, adjustment: AdjustmentType) -> str:
        """
        转换复权类型为 BaoStock 参数

        BaoStock adjustflag:
        - "3": 不复权（默认）
        - "1": 后复权
        - "2": 前复权
        """
        mapping = {
            AdjustmentType.NONE: "3",
            AdjustmentType.PREVIOUS: "2",  # 前复权
            AdjustmentType.POST: "1",  # 后复权
        }
        return mapping.get(adjustment, "3")

    def _get_market_type(self, code: str) -> MarketType:
        """根据代码判断市场类型"""
        full_code = self._ensure_full_code(code)

        if full_code.startswith("SH"):
            return MarketType.SH
        elif full_code.startswith("SZ"):
            return MarketType.SZ
        elif full_code.startswith("BJ"):
            return MarketType.BJ

        # 根据数字判断
        clean_code = full_code.replace("SH", "").replace("SZ", "").replace("BJ", "")
        if clean_code and clean_code[0].isdigit():
            first_digit = clean_code[0]
            if first_digit in ["6", "5"]:
                return MarketType.SH
            elif first_digit in ["0", "1", "2", "3"]:
                return MarketType.SZ

        return MarketType.SH
