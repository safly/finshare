# sources/base_source.py (完整代码)
import time
import random
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict

import requests

from finshare.config.settings import config
from finshare.models.data_models import HistoricalData, SnapshotData, AdjustmentType
from finshare.logger import logger

# User-Agent 池（模拟不同浏览器）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


class BaseDataSource(ABC):
    """数据源抽象基类"""

    # 类级别的冷却状态（所有实例共享）
    _cooldown_until: Dict[str, float] = {}  # source_name -> cooldown_end_timestamp
    # 类级别的请求时间记录（线程安全）
    _last_request_time: Dict[str, float] = {}  # source_name -> last_request_timestamp
    _rate_limit_lock = threading.Lock()  # 全局锁，确保请求间隔

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.base_url = None
        self.session = self._create_session()
        # 使用配置的请求间隔
        self.request_interval = config.data_source.request_interval
        self.request_jitter = 0.5  # 请求间隔随机抖动范围（±50%）

    @staticmethod
    def get_random_user_agent() -> str:
        """获取随机User-Agent"""
        return random.choice(USER_AGENTS)

    def _create_session(self):
        """创建HTTP会话（无重试，失败直接切换数据源）"""
        session = requests.Session()

        # 为 session 添加默认超时设置
        original_request = session.request

        def request_with_timeout(method, url, **kwargs):
            if "timeout" not in kwargs:
                kwargs["timeout"] = config.data_source.request_timeout
            return original_request(method, url, **kwargs)

        session.request = request_with_timeout

        return session

    def _rate_limit(self):
        """请求频率限制（线程安全，带随机抖动）"""
        # 计算带随机抖动的间隔时间
        jitter = random.uniform(-self.request_jitter, self.request_jitter)
        actual_interval = self.request_interval * (1 + jitter)
        actual_interval = max(0.5, actual_interval)  # 最小0.5秒

        with self._rate_limit_lock:
            last_time = self._last_request_time.get(self.source_name, 0)
            elapsed = time.time() - last_time
            if elapsed < actual_interval:
                sleep_time = actual_interval - elapsed
                # 先更新时间再释放锁，避免其他线程同时请求
                self._last_request_time[self.source_name] = time.time() + sleep_time
            else:
                sleep_time = 0
                self._last_request_time[self.source_name] = time.time()

        # 在锁外sleep，不阻塞其他数据源
        if sleep_time > 0:
            time.sleep(sleep_time)

    def is_in_cooldown(self) -> bool:
        """检查数据源是否处于冷却状态（24小时内不可用）"""
        cooldown_end = self._cooldown_until.get(self.source_name, 0)
        return time.time() < cooldown_end

    def get_cooldown_remaining(self) -> float:
        """获取剩余冷却时间（秒）"""
        cooldown_end = self._cooldown_until.get(self.source_name, 0)
        remaining = cooldown_end - time.time()
        return max(0, remaining)

    def _enter_cooldown(self, reason: str = "request_failed"):
        """进入冷却状态（固定24小时）"""
        cooldown_hours = config.data_source.failure_cooldown_hours
        cooldown_seconds = cooldown_hours * 3600

        self._cooldown_until[self.source_name] = time.time() + cooldown_seconds
        logger.warning(
            f"{self.source_name} 请求失败，进入冷却状态: {reason}, "
            f"冷却时间={cooldown_hours}小时，将切换到其他数据源"
        )

    @abstractmethod
    def get_historical_data(
        self,
        code: str,
        start_date: date,
        end_date: date,
        adjustment: AdjustmentType = AdjustmentType.NONE,
    ) -> List[HistoricalData]:
        """获取历史数据"""
        pass

    @abstractmethod
    def get_snapshot_data(self, code: str) -> Optional[SnapshotData]:
        """获取交易快照数据"""
        pass

    @abstractmethod
    def get_batch_snapshots(self, codes: List[str]) -> Dict[str, SnapshotData]:
        """批量获取快照数据"""
        pass

    def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """发送HTTP请求（失败直接进入24小时冷却，切换数据源）"""
        # 检查是否在冷却中
        if self.is_in_cooldown():
            remaining = self.get_cooldown_remaining()
            logger.debug(f"{self.source_name} 在冷却中，剩余 {remaining/3600:.1f}小时")
            return None

        self._rate_limit()

        # 合并请求头，使用随机User-Agent
        request_headers = {"User-Agent": self.get_random_user_agent()}
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.get(url, params=params, headers=request_headers)

            # 检测错误响应，直接进入冷却
            if response.status_code == 429:
                self._enter_cooldown("HTTP 429 Too Many Requests")
                return None

            if response.status_code == 403:
                self._enter_cooldown("HTTP 403 Forbidden")
                return None

            if response.status_code == 503:
                self._enter_cooldown("HTTP 503 Service Unavailable")
                return None

            if response.status_code >= 400:
                self._enter_cooldown(f"HTTP {response.status_code}")
                return None

            response.raise_for_status()

            # 尝试解析JSON，如果不是JSON则返回文本
            try:
                return response.json()
            except ValueError:
                return response.text

        except requests.RequestException as e:
            # 任何请求异常都进入冷却状态
            self._enter_cooldown(f"请求异常: {e}")
            return None

    def _ensure_full_code(self, code: str) -> str:
        """
        确保返回完整代码格式（子类应覆盖此方法）

        支持输入格式:
        - sz.159915 / sh.600519 (BaoStock格式) -> SZ159915 / SH600519
        - SZ159915 / SH600519 (标准格式) -> 保持不变
        - 159915 / 600519 (纯数字) -> 自动添加前缀

        返回格式: SH/SZ/BJ + 6位数字代码，如 SZ159915
        """
        if not code:
            return code

        code = code.strip()

        # 处理带点的格式 (如 sz.159915 / sh.600519)
        if "." in code:
            parts = code.split(".")
            if len(parts) == 2:
                market = parts[0].upper()
                num_code = parts[1]
                if market in ("SH", "SZ", "BJ", "HK", "US"):
                    return f"{market}{num_code}"

        # 如果已经带有市场前缀且不含点，直接返回大写
        upper_code = code.upper()
        if upper_code.startswith(("SH", "SZ", "BJ", "HK", "US")):
            for prefix in ("SH", "SZ", "BJ", "HK", "US"):
                if upper_code.startswith(prefix):
                    remaining = upper_code[len(prefix) :]
                    if remaining and remaining[0].isdigit():
                        return upper_code
                    if remaining.startswith("."):
                        return f"{prefix}{remaining[1:]}"

        # 尝试根据数字判断市场
        clean_code = code.replace("SH", "").replace("SZ", "").replace("BJ", "").replace(".", "")
        if clean_code and clean_code[0].isdigit():
            first_digit = clean_code[0]
            if first_digit in ["6", "5"]:
                return f"SH{clean_code}"
            elif first_digit in ["0", "1", "2", "3"]:
                return f"SZ{clean_code}"
            elif first_digit == "9":
                if clean_code.startswith("90"):
                    return f"SH{clean_code}"
                else:
                    return f"BJ{clean_code}"

        return code  # 无法确定，返回原样
