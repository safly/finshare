# sources/tencent_source.py (完整代码)
import json
import time
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import re

from finshare.sources.base_source import BaseDataSource
from finshare.models.data_models import HistoricalData, SnapshotData, AdjustmentType, MarketType
from finshare.logger import logger


class TencentDataSource(BaseDataSource):
    """腾讯财经数据源实现"""

    def __init__(self):
        super().__init__("tencent")
        self.base_url = "http://qt.gtimg.cn"
        self.historical_base_url = "http://web.ifzq.gtimg.cn"

        # 腾讯API配置
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "http://gu.qq.com/",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def get_historical_data(
        self,
        code: str,
        start_date: date,
        end_date: date,
        adjustment: AdjustmentType = AdjustmentType.NONE,
    ) -> List[HistoricalData]:
        """获取腾讯历史数据"""
        try:
            # 确保使用完整代码
            full_code = self._ensure_full_code(code)
            market_code = self._convert_code_format(full_code)

            # 腾讯前复权K线接口
            url = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"

            # 根据复权类型调整参数（腾讯API必须指定复权类型，默认前复权）
            if adjustment == AdjustmentType.POST:
                fq_type = "hfq"  # 后复权
            else:
                fq_type = "qfq"  # 前复权（默认）

            # 参数格式：代码,周期,起始日期,结束日期,数量,复权类型
            fq_suffix = f",{fq_type}"
            params = {
                "param": f"{market_code},day,,,1000{fq_suffix}",
                "_var": f"kline_day{fq_type}",
            }

            logger.debug(f"腾讯历史数据请求参数: {params}")

            # 使用基类的 _make_request 方法
            response_data = self._make_request(url, params)

            if not response_data:
                logger.warning(f"腾讯历史数据请求无响应: {full_code}")
                return []

            # 解析腾讯数据
            data = self._parse_tencent_response(response_data, market_code)

            if not data or not isinstance(data, list):
                logger.warning(f"腾讯历史数据解析失败: {full_code}")
                return []

            # 解析历史数据
            historical_data = self._parse_tencent_historical_data(data, full_code, adjustment)

            # 按日期筛选
            filtered_data = [d for d in historical_data if start_date <= d.trade_date <= end_date]

            if filtered_data:
                logger.debug(f"腾讯历史数据获取成功: {full_code}, 共{len(filtered_data)}条数据")
            else:
                logger.warning(f"腾讯历史数据获取但无有效数据: {full_code}")

            return filtered_data

        except Exception as e:
            error_msg = f"获取腾讯历史数据失败 {code}: {e}"
            logger.error(error_msg)
            return []

    def _parse_tencent_response(self, response_data: Any, market_code: str) -> Any:
        """解析腾讯响应数据"""
        try:
            # 腾讯返回的是JSONP格式
            if isinstance(response_data, str):
                # 查找JSON部分
                json_match = re.search(r"\{.*\}", response_data)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)

                    # 腾讯API返回格式: {"code":0,"data":{"sz000001":{"qfqday":[[...]]}}
                    if "data" not in data:
                        return None

                    stock_data = data["data"].get(market_code, {})

                    # 如果没找到，尝试添加 hk 前缀（港股）
                    if not stock_data and market_code.startswith("sh"):
                        hk_code = "hk" + market_code[2:]
                        stock_data = data["data"].get(hk_code, {})

                    # 根据复权类型获取数据
                    fq_match = re.search(r"kline_day(qfq|hfq)", response_data)
                    if fq_match:
                        fq_type = fq_match.group(1)
                        kline_key = f"{fq_type}day"  # qfqday 或 hfqday
                    else:
                        kline_key = "day"  # 不复权

                    return stock_data.get(kline_key) or stock_data.get("day")

            return None

        except Exception as e:
            logger.error(f"解析腾讯响应失败: {e}")
            return None

    def _parse_tencent_historical_data(
        self, raw_data: List[List], code: str, adjustment: AdjustmentType
    ) -> List[HistoricalData]:
        """解析腾讯历史数据格式"""
        historical_list = []

        # 确保使用完整代码
        full_code = self._ensure_full_code(code)

        for item in raw_data:
            try:
                # 腾讯格式: [日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, ...]
                if len(item) < 6:
                    continue

                date_str = item[0]

                # 解析日期
                try:
                    trade_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue

                # 腾讯数据顺序
                open_price = float(item[1])
                close_price = float(item[2])
                high_price = float(item[3])
                low_price = float(item[4])
                volume = float(item[5])
                amount = float(item[6]) if len(item) > 6 else 0

                # 复权因子（腾讯不直接提供）
                adjust_factor = 1.0

                # 创建历史数据对象
                historical_data = HistoricalData(
                    code=full_code,
                    trade_date=trade_date,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume,
                    amount=amount,
                    adjust_factor=adjust_factor,
                    market=self._get_market_type(full_code),
                    adjustment=adjustment,
                    data_source=self.source_name,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                historical_list.append(historical_data)

            except (ValueError, TypeError, IndexError) as e:
                logger.debug(f"解析腾讯历史数据条目失败: {e}")
                continue

        return historical_list

    def get_snapshot_data(self, code: str) -> Optional[SnapshotData]:
        """获取腾讯实时快照数据"""
        try:
            # 确保使用完整代码
            full_code = self._ensure_full_code(code)
            market_code = self._convert_code_format(full_code)
            url = f"{self.base_url}/q={market_code}"

            response_data = self._make_request(url)

            if not response_data:
                return None

            snapshot = self._parse_tencent_snapshot(response_data, full_code)

            if snapshot:
                logger.debug(f"腾讯快照数据获取成功: {full_code}")

            return snapshot

        except Exception as e:
            error_msg = f"获取腾讯快照数据失败 {code}: {e}"
            logger.error(error_msg)
            return None

    def get_batch_snapshots(self, codes: List[str]) -> Dict[str, SnapshotData]:
        """批量获取腾讯快照数据"""
        results = {}

        # 确保使用完整代码
        full_codes = [self._ensure_full_code(code) for code in codes]

        batch_size = 100  # 腾讯API支持批量

        for i in range(0, len(full_codes), batch_size):
            batch = full_codes[i : i + batch_size]
            market_codes = [self._convert_code_format(code) for code in batch]

            # 腾讯API支持逗号分隔的多个代码
            query_str = ",".join(market_codes)
            url = f"{self.base_url}/q={query_str}"

            response_data = self._make_request(url)
            if response_data:
                parsed_data = self._parse_tencent_batch_snapshots(response_data, batch)
                results.update(parsed_data)

            # 避免请求过快
            time.sleep(5)

        return results

    def _parse_tencent_snapshot(self, content: str, code: str) -> Optional[SnapshotData]:
        """解析腾讯快照数据格式"""
        try:
            # 确保使用完整代码
            full_code = self._ensure_full_code(code)

            # 腾讯格式: v_sh600000="平安银行~12.34~12.35~...";
            pattern = r'v_(sh|sz)(\d+)=["\'](.*?)["\']'
            matches = re.findall(pattern, content)

            if not matches:
                return None

            for market_prefix, code_num, data_str in matches:
                clean_target = full_code.replace("SH", "").replace("SZ", "").replace("BJ", "")
                if code_num != clean_target:
                    continue

                data_parts = data_str.split("~")
                if len(data_parts) < 30:
                    continue

                # 解析字段
                stock_name = data_parts[0]
                current_price = float(data_parts[3]) if data_parts[3] else 0.0
                pre_close = float(data_parts[4]) if data_parts[4] else 0.0
                open_price = float(data_parts[5]) if data_parts[5] else 0.0
                volume = float(data_parts[6]) if data_parts[6] else 0.0
                bid_price = float(data_parts[9]) if data_parts[9] else 0.0
                ask_price = float(data_parts[19]) if data_parts[19] else 0.0
                high_price = (
                    float(data_parts[33]) if len(data_parts) > 33 and data_parts[33] else 0.0
                )
                low_price = (
                    float(data_parts[34]) if len(data_parts) > 34 and data_parts[34] else 0.0
                )
                # 成交额（万元转元）
                amount = (
                    float(data_parts[37]) * 10000
                    if len(data_parts) > 37 and data_parts[37]
                    else 0.0
                )

                snapshot = SnapshotData(
                    code=full_code,
                    timestamp=datetime.now(),
                    last_price=current_price,
                    volume=volume,  # 单位：手
                    amount=amount,  # 单位：元
                    bid1_price=bid_price,
                    ask1_price=ask_price,
                    bid1_volume=float(data_parts[10]) if len(data_parts) > 10 else 0,
                    ask1_volume=float(data_parts[20]) if len(data_parts) > 20 else 0,
                    day_high=high_price,
                    day_low=low_price,
                    day_open=open_price,
                    prev_close=pre_close,
                    is_trading=current_price > 0,
                    market=self._get_market_type(full_code),
                    data_source=self.source_name,
                )

                return snapshot

        except Exception as e:
            logger.error(f"解析腾讯快照数据失败: {e}")

        return None

    def _parse_tencent_batch_snapshots(
        self, content: str, codes: List[str]
    ) -> Dict[str, SnapshotData]:
        """解析腾讯批量快照数据"""
        results = {}

        # 按行分割
        lines = content.strip().split(";")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 匹配格式: v_sh600000="数据...";
            pattern = r'v_(sh|sz)(\d+)=["\'](.*?)["\']'
            match = re.search(pattern, line)

            if not match:
                continue

            market_prefix = match.group(1)
            code_num = match.group(2)
            data_str = match.group(3)

            # 构造标准代码
            if market_prefix == "sh":
                full_code = f"SH{code_num}"
            elif market_prefix == "sz":
                full_code = f"SZ{code_num}"
            elif market_prefix == "bj":
                full_code = f"BJ{code_num}"
            else:
                continue

            # 只处理请求的代码
            if full_code not in codes:
                # 尝试查找不带前缀的版本
                for request_code in codes:
                    if (
                        request_code.replace("SH", "").replace("SZ", "").replace("BJ", "")
                        == code_num
                    ):
                        full_code = request_code
                        break
                else:
                    continue

            # 解析单条数据
            snapshot = self._parse_tencent_snapshot(line, full_code)
            if snapshot:
                results[full_code] = snapshot

        return results

    def _convert_code_format(self, code: str) -> str:
        """转换代码格式为腾讯API格式"""
        # 确保使用完整代码
        full_code = self._ensure_full_code(code)

        # 先移除 .HK .SH .SZ .BJ .US 后缀
        clean_code = full_code.replace(".HK", "").replace(".SH", "").replace(".SZ", "").replace(".BJ", "").replace(".US", "")

        # 移除可能的交易所前缀
        clean_code = clean_code.replace("HK", "").replace("SH", "").replace("SZ", "").replace("BJ", "").replace("US", "")

        # 判断市场并添加前缀
        if full_code.startswith("HK") or ".HK" in full_code:
            return f"hk{clean_code}"
        elif full_code.startswith("US") or ".US" in full_code:
            return f"us{clean_code}"
        elif full_code.startswith("SH") or ".SH" in full_code:
            return f"sh{clean_code}"
        elif full_code.startswith("SZ") or ".SZ" in full_code:
            return f"sz{clean_code}"
        elif full_code.startswith("BJ") or ".BJ" in full_code:
            return f"bj{clean_code}"
        elif clean_code and clean_code[0] in ["6", "5"]:
            return f"sh{clean_code}"
        elif clean_code and clean_code[0] in ["0", "1", "2", "3"]:
            return f"sz{clean_code}"
        else:
            return code

    def _get_market_type(self, code: str) -> MarketType:
        """根据代码判断市场类型"""
        # 确保使用完整代码
        full_code = self._ensure_full_code(code)

        if full_code.startswith("SH"):
            return MarketType.SH
        elif full_code.startswith("SZ"):
            return MarketType.SZ
        elif full_code.startswith("BJ"):
            return MarketType.BJ
        else:
            # 根据数字判断
            clean_code = full_code.replace("SH", "").replace("SZ", "").replace("BJ", "")
            if clean_code and clean_code[0].isdigit():
                first_digit = clean_code[0]
                if first_digit in ["6", "5"]:
                    return MarketType.SH
                elif first_digit in ["0", "1", "2", "3"]:
                    return MarketType.SZ
                elif first_digit == "9":
                    if clean_code.startswith("90"):
                        return MarketType.SH
                    else:
                        return MarketType.BJ

        return MarketType.SH
