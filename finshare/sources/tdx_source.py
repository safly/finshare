# sources/tdx_source.py
"""
通达信 (pytdx) 数据源实现

功能：实时行情数据获取（速度快）
特点：连接通达信公共服务器，无需登录
限制：历史K线不支持复权，单次最多800条

GitHub: https://github.com/rainx/pytdx
"""

import random
import threading
from datetime import date, datetime
from typing import List, Optional, Dict

from finshare.models.data_models import HistoricalData, SnapshotData, AdjustmentType, MarketType
from finshare.logger import logger
from finshare.sources.base_source import BaseDataSource

# 延迟导入 pytdx，避免未安装时报错
_pytdx_available = None
_TdxHq_API = None

# 通达信公共行情服务器列表
TDX_SERVERS = [
    ("119.147.212.81", 7709),  # 深圳双线主站
    ("112.74.214.43", 7727),  # 深圳双线主站2
    ("221.231.141.60", 7709),  # 南京电信主站
    ("101.227.73.20", 7709),  # 上海电信主站
    ("101.227.77.254", 7709),  # 上海电信主站2
    ("14.215.128.18", 7709),  # 深圳移动主站
    ("59.173.18.140", 7709),  # 武汉电信主站
    ("218.75.126.9", 7709),  # 杭州电信主站
    ("115.238.56.198", 7709),  # 杭州电信主站2
    ("124.160.88.183", 7709),  # 杭州移动主站
]


def _ensure_pytdx():
    """确保 pytdx 已导入"""
    global _pytdx_available, _TdxHq_API

    if _pytdx_available is None:
        try:
            from pytdx.hq import TdxHq_API

            _TdxHq_API = TdxHq_API
            _pytdx_available = True
        except ImportError:
            _pytdx_available = False
            logger.warning("pytdx 未安装，请运行: pip install pytdx")

    return _pytdx_available


class TdxDataSource(BaseDataSource):
    """
    通达信数据源实现

    主要用途：获取实时行情数据（速度快）
    不推荐用途：历史K线（不支持复权）
    """

    def __init__(self):
        super().__init__("tdx")
        self._api = None
        self._connected = False
        self._lock = threading.Lock()
        self._current_server = None

    def _ensure_connected(self) -> bool:
        """确保已连接到服务器"""
        if not _ensure_pytdx():
            return False

        with self._lock:
            if self._connected and self._api:
                return True

            # 尝试连接服务器
            self._api = _TdxHq_API()

            # 随机打乱服务器顺序，负载均衡
            servers = TDX_SERVERS.copy()
            random.shuffle(servers)

            for host, port in servers:
                try:
                    if self._api.connect(host, port):
                        self._connected = True
                        self._current_server = (host, port)
                        logger.info(f"[TDX] 连接成功: {host}:{port}")
                        return True
                except Exception as e:
                    logger.debug(f"[TDX] 连接 {host}:{port} 失败: {e}")
                    continue

            logger.error("[TDX] 所有服务器连接失败")
            return False

    def _reconnect(self) -> bool:
        """重新连接"""
        with self._lock:
            self._connected = False
            if self._api:
                try:
                    self._api.disconnect()
                except:
                    pass
                self._api = None

        return self._ensure_connected()

    def get_historical_data(
        self,
        code: str,
        start_date: date,
        end_date: date,
        adjustment: AdjustmentType = AdjustmentType.NONE,
    ) -> List[HistoricalData]:
        """
        获取历史K线数据

        注意：通达信原始数据不支持复权，返回的是不复权数据
        如需复权数据，建议使用 BaoStock
        """
        if adjustment != AdjustmentType.NONE:
            logger.warning("[TDX] 不支持复权数据，将返回不复权数据。如需复权请使用BaoStock")

        if not self._ensure_connected():
            return []

        if self.is_in_cooldown():
            return []

        try:
            market, clean_code = self._parse_code(code)
            full_code = self._ensure_full_code(code)

            self._rate_limit()

            # 计算需要获取的天数
            days = (end_date - start_date).days + 1
            historical_list = []

            # pytdx 单次最多获取800条，需要分批
            offset = 0
            batch_size = 800

            while True:
                data = self._api.get_security_bars(
                    category=9,  # 日K线
                    market=market,
                    code=clean_code,
                    start=offset,
                    count=batch_size,
                )

                if not data:
                    break

                # 获取价格除数（ETF/LOF需要除以10）
                price_divisor = self._get_price_divisor(full_code)

                for item in data:
                    try:
                        trade_date = datetime.strptime(item["datetime"], "%Y-%m-%d").date()

                        # 过滤日期范围
                        if trade_date < start_date:
                            continue
                        if trade_date > end_date:
                            continue

                        hist_data = HistoricalData(
                            code=full_code,
                            trade_date=trade_date,
                            open_price=float(item["open"]) / price_divisor,
                            high_price=float(item["high"]) / price_divisor,
                            low_price=float(item["low"]) / price_divisor,
                            close_price=float(item["close"]) / price_divisor,
                            volume=float(item["vol"]),  # 通达信返回的已经是手
                            amount=float(item["amount"]),
                            adjust_factor=1.0,
                            market=self._get_market_type(full_code),
                            adjustment=AdjustmentType.NONE,  # 通达信不支持复权
                            data_source=self.source_name,
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                        )
                        historical_list.append(hist_data)
                    except Exception as e:
                        logger.debug(f"解析TDX历史数据失败: {e}")
                        continue

                # 如果返回数据少于请求数量，说明已到头
                if len(data) < batch_size:
                    break

                offset += batch_size

                # 如果已获取足够数据，退出
                if len(historical_list) >= days:
                    break

            # 按日期排序
            historical_list.sort(key=lambda x: x.trade_date)

            logger.info(f"[TDX] 获取历史数据成功: {full_code}, 共{len(historical_list)}条")
            return historical_list

        except Exception as e:
            logger.error(f"[TDX] 获取历史数据失败 {code}: {e}")
            self._reconnect()
            return []

    def get_snapshot_data(self, code: str) -> Optional[SnapshotData]:
        """获取实时快照数据"""
        if not self._ensure_connected():
            return None

        if self.is_in_cooldown():
            return None

        try:
            market, clean_code = self._parse_code(code)
            full_code = self._ensure_full_code(code)

            self._rate_limit()

            # 获取实时行情
            data = self._api.get_security_quotes([(market, clean_code)])

            if not data or len(data) == 0:
                return None

            item = data[0]
            return self._parse_quote(item, full_code)

        except Exception as e:
            logger.error(f"[TDX] 获取快照失败 {code}: {e}")
            self._reconnect()
            return None

    def _parse_quote(self, item: dict, code: str) -> Optional[SnapshotData]:
        """
        解析实时行情数据

        通达信数据单位：
        - 股票价格: 元
        - ETF/LOF价格: 需要除以10（通达信返回的是10倍值）
        - 成交量: 手（直接使用，无需转换）
        - 成交额: 元
        """
        try:
            # 获取价格除数（ETF/LOF需要除以10）
            price_divisor = self._get_price_divisor(code)

            last_price = float(item.get("price", 0)) / price_divisor
            day_high = float(item.get("high", 0)) / price_divisor
            day_low = float(item.get("low", 0)) / price_divisor
            day_open = float(item.get("open", 0)) / price_divisor
            prev_close = float(item.get("last_close", 0)) / price_divisor
            bid1_price = float(item.get("bid1", 0)) / price_divisor
            ask1_price = float(item.get("ask1", 0)) / price_divisor

            return SnapshotData(
                code=code,
                timestamp=datetime.now(),
                last_price=last_price,
                volume=float(item.get("vol", 0)),  # 通达信返回的已经是手
                amount=float(item.get("amount", 0)),
                bid1_price=bid1_price,
                ask1_price=ask1_price,
                bid1_volume=float(item.get("bid_vol1", 0)),  # 已经是手
                ask1_volume=float(item.get("ask_vol1", 0)),  # 已经是手
                day_high=day_high,
                day_low=day_low,
                day_open=day_open,
                prev_close=prev_close,
                is_trading=last_price > 0,
                market=self._get_market_type(code),
                data_source=self.source_name,
            )
        except Exception as e:
            logger.debug(f"解析TDX快照失败: {e}")
            return None

    def _get_price_divisor(self, code: str) -> float:
        """
        获取价格除数

        通达信对于不同类型证券返回的价格单位不同：
        - 股票: 直接是元
        - ETF/LOF/基金: 返回值是10倍，需要除以10
        """
        full_code = self._ensure_full_code(code)
        clean_code = full_code.replace("SH", "").replace("SZ", "").replace("BJ", "")

        if not clean_code:
            return 1.0

        # ETF/LOF/基金代码规则：
        # 深圳：15xxxx (ETF), 16xxxx (LOF)
        # 上海：50xxxx (LOF), 51xxxx (ETF), 52xxxx, 56xxxx, 58xxxx, 59xxxx
        fund_prefixes = ("15", "16", "50", "51", "52", "56", "58", "59")

        if clean_code.startswith(fund_prefixes):
            return 10.0  # ETF/LOF/基金需要除以10

        return 1.0  # 股票直接使用

    def get_batch_snapshots(self, codes: List[str]) -> Dict[str, SnapshotData]:
        """批量获取快照数据"""
        if not self._ensure_connected():
            return {}

        if self.is_in_cooldown():
            return {}

        results = {}

        try:
            # 转换代码格式
            code_list = []
            code_mapping = {}
            for code in codes:
                market, clean_code = self._parse_code(code)
                full_code = self._ensure_full_code(code)
                code_list.append((market, clean_code))
                code_mapping[(market, clean_code)] = full_code

            self._rate_limit()

            # pytdx 支持批量查询，但建议分批（每批不超过80个）
            batch_size = 80
            for i in range(0, len(code_list), batch_size):
                batch = code_list[i : i + batch_size]

                data = self._api.get_security_quotes(batch)

                if data:
                    for item in data:
                        try:
                            market = item.get("market", 0)
                            clean_code = item.get("code", "")
                            full_code = code_mapping.get((market, clean_code))

                            if not full_code:
                                # 尝试从原始代码找
                                full_code = self._ensure_full_code(clean_code)

                            snapshot = self._parse_quote(item, full_code)
                            if snapshot:
                                results[full_code] = snapshot
                        except Exception as e:
                            logger.debug(f"解析批量快照条目失败: {e}")
                            continue

            logger.info(f"[TDX] 批量获取快照: {len(results)}/{len(codes)} 成功")
            return results

        except Exception as e:
            logger.error(f"[TDX] 批量获取快照失败: {e}")
            self._reconnect()
            return {}

    def _parse_code(self, code: str) -> tuple:
        """
        解析代码，返回 (市场, 纯代码)

        通达信市场代码:
        - 0: 深圳
        - 1: 上海
        """
        full_code = self._ensure_full_code(code)

        if full_code.startswith("SH"):
            return (1, full_code[2:])
        elif full_code.startswith("SZ"):
            return (0, full_code[2:])
        elif full_code.startswith("BJ"):
            return (0, full_code[2:])  # 北交所暂用深圳
        else:
            # 根据数字判断
            clean_code = full_code.replace("SH", "").replace("SZ", "").replace("BJ", "")
            if clean_code and clean_code[0].isdigit():
                first_digit = clean_code[0]
                if first_digit in ["6", "5"]:
                    return (1, clean_code)  # 上海
                elif first_digit in ["0", "1", "2", "3"]:
                    return (0, clean_code)  # 深圳

            return (1, clean_code)  # 默认上海

    def _get_market_type(self, code: str) -> MarketType:
        """根据代码判断市场类型"""
        full_code = self._ensure_full_code(code)

        if full_code.startswith("SH"):
            return MarketType.SH
        elif full_code.startswith("SZ"):
            return MarketType.SZ
        elif full_code.startswith("BJ"):
            return MarketType.BJ

        clean_code = full_code.replace("SH", "").replace("SZ", "").replace("BJ", "")
        if clean_code and clean_code[0].isdigit():
            first_digit = clean_code[0]
            if first_digit in ["6", "5"]:
                return MarketType.SH
            elif first_digit in ["0", "1", "2", "3"]:
                return MarketType.SZ

        return MarketType.SH

    def disconnect(self):
        """断开连接"""
        with self._lock:
            if self._api:
                try:
                    self._api.disconnect()
                except:
                    pass
                self._api = None
            self._connected = False
            logger.info("[TDX] 已断开连接")

    def __del__(self):
        """析构函数，确保断开连接"""
        self.disconnect()
