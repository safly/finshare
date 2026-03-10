from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


class AdjustmentType(str, Enum):
    """复权类型"""
    NONE = "none"
    PREVIOUS = "pre"
    POST = "post"


class MarketType(str, Enum):
    """市场类型"""
    SH = "sh"
    SZ = "sz"
    BJ = "bj"
    HK = "hk"
    US = "us"


class FrequencyType(str, Enum):
    """K线频率"""
    MIN_1 = "1"
    MIN_5 = "5"
    MIN_15 = "15"
    MIN_30 = "30"
    MIN_60 = "60"
    DAILY = "d"
    WEEKLY = "w"
    MONTHLY = "m"


# ============ 分钟线数据模型 ============

class MinuteData(BaseModel):
    """
    分钟线数据

    字段说明:
    - fs_code: 股票代码 (000001.SZ)
    - trade_time: 交易时间 (YYYYMMDDHHMMSS)
    - open/high/low/close: 价格 (元)
    - volume: 成交量 (股)
    - amount: 成交金额 (元)
    """

    fs_code: str = Field(..., description="股票代码: 000001.SZ")
    trade_time: str = Field(..., description="交易时间: YYYYMMDDHHMMSS")

    # 行情数据
    open: float = Field(..., description="开盘价(元)")
    close: float = Field(..., description="收盘价(元)")
    high: float = Field(..., description="最高价(元)")
    low: float = Field(..., description="最低价(元)")

    # 量价数据
    volume: int = Field(..., description="成交量(股)")
    amount: float = Field(0.0, description="成交金额(元)")

    # 元数据
    frequency: str = Field("5", description="频率: 1/5/15/30/60")
    data_source: str = Field(default="unknown", description="数据源")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        extra="ignore",
    )


class HistoricalData(BaseModel):
    """
    历史数据模型 - 安全配置版
    关键修改：
    1. 移除了所有`alias`，避免潜在的解析循环。
    2. 将易冲突的字段名（open, close, date）改为更安全的名称。
    3. 使用最简配置。
    """

    # 核心行情字段
    code: str
    trade_date: date = Field(..., description="交易日期")
    open_price: float = Field(..., description="开盘价")
    high_price: float = Field(..., description="最高价")
    low_price: float = Field(..., description="最低价")
    close_price: float = Field(..., description="收盘价")
    volume: float = Field(..., description="成交量")

    # 可选字段
    amount: Optional[float] = Field(None, description="成交额")
    adjust_factor: Optional[float] = Field(
        default=1.0, description="复权因子", alias="adjustment_factor"  # 添加别名
    )
    turnover_rate: Optional[float] = Field(None, description="换手率")

    # 元数据字段
    market: MarketType = Field(default=MarketType.SH, description="市场类型")
    adjustment: AdjustmentType = Field(default=AdjustmentType.NONE, description="复权类型")
    data_source: str = Field(default="unknown", description="数据来源")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # Pydantic V2 配置 - 启用别名支持
    model_config = ConfigDict(
        # 启用别名支持
        populate_by_name=True,
        # 确保json序列化
        json_encoders={datetime: lambda v: v.isoformat(), date: lambda v: v.isoformat()},
        # 可以改为'ignore'以避免类似问题，或者保持'forbid'但确保字段对齐
        extra="ignore",
    )

    @field_validator("trade_date")
    def validate_trade_date(cls, v: date) -> date:
        """验证日期不超过今天"""
        if v > date.today():
            raise ValueError("交易日期不能晚于今天")
        return v


class SnapshotData(BaseModel):
    """
    交易快照数据模型 - 安全配置版
    """

    # 核心快照字段
    code: str
    timestamp: datetime
    last_price: float = Field(..., description="最新价")  # 改名：price -> last_price
    volume: float
    amount: float

    # 盘口字段 (可选)
    bid1_price: Optional[float] = Field(None, description="买一价")  # 改名：bid_price
    ask1_price: Optional[float] = Field(None, description="卖一价")  # 改名：ask_price
    bid1_volume: Optional[float] = Field(None, description="买一量")
    ask1_volume: Optional[float] = Field(None, description="卖一量")

    # 日内指标 (可选)
    day_high: Optional[float] = Field(None, description="当日最高")  # 改名：high
    day_low: Optional[float] = Field(None, description="当日最低")  # 改名：low
    day_open: Optional[float] = Field(None, description="开盘价")  # 改名：open

    # 市场状态
    is_trading: bool = Field(default=True, description="是否在交易中")
    prev_close: Optional[float] = Field(None, description="前收盘价")  # 改名：pre_close

    # 元数据
    market: MarketType = Field(default=MarketType.SH, description="市场类型")
    data_source: str = Field(default="unknown", description="数据来源")

    # Pydantic V2 配置
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()}, extra="forbid")

    @field_validator("timestamp")
    def validate_timestamp(cls, v: datetime) -> datetime:
        """验证时间戳不超过当前时间"""
        if v > datetime.now():
            raise ValueError("时间戳不能晚于当前时间")
        return v

    @property
    def change(self) -> Optional[float]:
        """涨跌额"""
        if self.last_price and self.prev_close:
            return round(self.last_price - self.prev_close, 2)
        return None

    @property
    def change_pct(self) -> Optional[float]:
        """涨跌幅(%)"""
        if self.last_price and self.prev_close and self.prev_close != 0:
            return round((self.last_price - self.prev_close) / self.prev_close * 100, 2)
        return None


class DataSourceStatus(BaseModel):
    source_name: str
    last_success_time: Optional[datetime]
    last_error_time: Optional[datetime]
    error_count: int = 0
    is_active: bool = True
    cool_down_until: Optional[datetime] = None

    @property
    def is_in_cool_down(self) -> bool:
        if not self.cool_down_until:
            return False
        return datetime.now() < self.cool_down_until


# ============ 期货数据模型 ============


class FutureExchange(str, Enum):
    """期货交易所"""
    CFFEX = "cffex"  # 中金所 (股指期货)
    SHFE = "shfe"    # 上期所 (金属、能源)
    DCE = "dce"     # 大商所 (农产品)
    CZCE = "czce"   # 郑商所 (化工、农产品)
    INE = "ine"     # 上期能源 (原油)


class FutureData(BaseModel):
    """
    期货历史数据模型

    字段说明:
    - code: 期货合约代码 (如 IF2409, CU2409)
    - trade_date: 交易日期
    - open_price: 开盘价
    - high_price: 最高价
    - low_price: 最低价
    - close_price: 收盘价
    - volume: 成交量 (手)
    - amount: 成交额 (元)
    - open_interest: 持仓量
    - settle_price: 结算价
    - pre_settle: 昨结算价
    """

    code: str = Field(..., description="期货合约代码")
    trade_date: date = Field(..., description="交易日期")
    open_price: float = Field(..., description="开盘价")
    high_price: float = Field(..., description="最高价")
    low_price: float = Field(..., description="最低价")
    close_price: float = Field(..., description="收盘价")
    volume: float = Field(..., description="成交量(手)")
    amount: Optional[float] = Field(None, description="成交额(元)")
    open_interest: Optional[float] = Field(None, description="持仓量(手)")
    settle_price: Optional[float] = Field(None, description="结算价")
    pre_settle: Optional[float] = Field(None, description="昨结算价")

    # 元数据
    exchange: FutureExchange = Field(default=FutureExchange.SHFE, description="交易所")
    contract_name: Optional[str] = Field(None, description="合约名称")
    data_source: str = Field(default="unknown", description="数据来源")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat(), date: lambda v: v.isoformat()},
        extra="ignore",
    )

    @field_validator("trade_date")
    def validate_trade_date(cls, v: date) -> date:
        """验证日期不超过今天"""
        if v > date.today():
            raise ValueError("交易日期不能晚于今天")
        return v


class FutureSnapshotData(BaseModel):
    """
    期货实时快照数据模型

    字段说明:
    - code: 期货合约代码
    - timestamp: 更新时间
    - last_price: 最新价
    - bid1_price: 买一价
    - ask1_price: 卖一价
    - volume: 成交量
    - open_interest: 持仓量
    """

    code: str = Field(..., description="期货合约代码")
    timestamp: datetime = Field(..., description="更新时间")
    last_price: float = Field(..., description="最新价")
    volume: float = Field(0, description="成交量(手)")
    open_interest: Optional[float] = Field(None, description="持仓量(手)")
    amount: Optional[float] = Field(None, description="成交额(元)")

    # 盘口
    bid1_price: Optional[float] = Field(None, description="买一价")
    ask1_price: Optional[float] = Field(None, description="卖一价")
    bid1_volume: Optional[float] = Field(None, description="买一量")
    ask1_volume: Optional[float] = Field(None, description="卖一量")

    # 日内
    day_high: Optional[float] = Field(None, description="当日最高")
    day_low: Optional[float] = Field(None, description="当日最低")
    day_open: Optional[float] = Field(None, description="开盘价")
    prev_close: Optional[float] = Field(None, description="前收盘价")

    # 元数据
    exchange: FutureExchange = Field(default=FutureExchange.SHFE, description="交易所")
    data_source: str = Field(default="unknown", description="数据来源")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        extra="ignore",
    )

    @property
    def change(self) -> Optional[float]:
        """涨跌额"""
        if self.last_price and self.prev_close:
            return round(self.last_price - self.prev_close, 2)
        return None

    @property
    def change_pct(self) -> Optional[float]:
        """涨跌幅(%)"""
        if self.last_price and self.prev_close and self.prev_close != 0:
            return round((self.last_price - self.prev_close) / self.prev_close * 100, 2)
        return None


# ============ 基金数据模型 ============


class FundData(BaseModel):
    """
    基金净值数据模型

    字段说明:
    - code: 基金代码 (如 161039)
    - name: 基金名称
    - nav: 单位净值
    - nav_acc: 累计净值
    - change: 涨跌额
    - change_pct: 涨跌幅
    - nav_date: 净值日期
    """

    code: str = Field(..., description="基金代码")
    name: Optional[str] = Field(None, description="基金名称")
    nav: float = Field(..., description="单位净值")
    nav_acc: Optional[float] = Field(None, description="累计净值")
    change: Optional[float] = Field(None, description="涨跌额")
    change_pct: Optional[float] = Field(None, description="涨跌幅(%)")
    nav_date: date = Field(..., description="净值日期")

    # 可选字段
    unit_nav: Optional[float] = Field(None, description="万份收益")
    accum_nav: Optional[float] = Field(None, description="七日年化收益率(%)")

    # 元数据
    data_source: str = Field(default="unknown", description="数据来源")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat(), date: lambda v: v.isoformat()},
        extra="ignore",
    )

    @field_validator("nav_date")
    def validate_nav_date(cls, v: date) -> date:
        """验证日期不超过今天"""
        if v > date.today():
            raise ValueError("净值日期不能晚于今天")
        return v
