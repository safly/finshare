"""
finshare Config Module

配置管理模块
"""

import os


class LoggingConfig:
    """日志配置"""

    def __init__(self):
        self.log_dir = os.path.join(os.path.expanduser("~"), ".finshare", "logs")
        self.log_level = "INFO"
        self.log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        self.rotation = "10 MB"
        self.retention = "30 days"
        self.enable_remote_logging = False
        self.remote_log_url = None


class DataSourceConfig:
    """数据源配置"""

    def __init__(self):
        self.source_priority = ["eastmoney", "tencent", "sina", "tdx", "baostock"]
        self.timeout = 30
        self.request_timeout = 30  # 请求超时时间（秒）
        self.retry_times = 3
        self.request_interval = 0.1  # 请求间隔（秒）
        self.max_workers = 5  # 最大并发数
        self.failure_cooldown_hours = 24  # 数据源失败后的冷却时间（小时）


class Config:
    """全局配置"""

    def __init__(self):
        self.timeout = 30
        self.logging = LoggingConfig()
        self.data_source = DataSourceConfig()

    def get(self, key, default=None):
        """获取配置项"""
        return getattr(self, key, default)


# 全局配置实例
config = Config()

__all__ = ["Config", "config"]
