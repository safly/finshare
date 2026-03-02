import sys
import os
from pathlib import Path
from loguru import logger

from finshare.config.settings import config


def _get_user_base_dir() -> Path:
    """获取用户可写基础目录"""
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MeepoQuant"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "MeepoQuant"
        return Path.home() / "AppData" / "Roaming" / "MeepoQuant"
    return Path.home() / ".meepo_quant"


def _is_packaged_runtime() -> bool:
    """检测是否为打包运行环境（PyInstaller/Nuitka/.app）"""
    if getattr(sys, "frozen", False):
        return True
    if "__compiled__" in dir():  # Nuitka
        return True
    exe_path = str(Path(sys.executable)).lower()
    if ".app/contents/macos" in exe_path:
        return True
    return False


def get_log_dir() -> Path:
    """获取日志目录，打包后使用用户目录"""
    # 打包后固定使用用户目录，规避 macOS App Translocation 只读问题
    if _is_packaged_runtime():
        return _get_user_base_dir() / "logs"

    # 开发环境使用配置目录；如果不可写则回退用户目录
    configured = Path(config.logging.log_dir)
    if configured.is_absolute():
        return configured
    return configured


class StockDataLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self._setup_logger()

    def _setup_logger(self):
        preferred_log_dir = get_log_dir()
        log_dir = preferred_log_dir
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # 回退到用户可写目录，避免打包后只读文件系统导致启动失败
            log_dir = _get_user_base_dir() / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

        logger.remove()

        logger.add(
            sys.stderr,
            format=config.logging.log_format,
            level=config.logging.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

        log_file = log_dir / "stock_data_{time:YYYY-MM-DD}.log"

        logger.add(
            log_file,
            format=config.logging.log_format,
            level=config.logging.log_level,
            rotation="00:00",  # 每天午夜轮转，确保跨天时自动创建新文件
            retention=config.logging.retention,
            compression="zip",
            encoding="utf-8",
            enqueue=True,
        )

        error_log = log_dir / "error_{time:YYYY-MM-DD}.log"
        logger.add(
            error_log,
            format=config.logging.log_format,
            level="ERROR",
            rotation="00:00",  # 每天午夜轮转
            retention="90 days",
            compression="zip",
        )

        perf_log = log_dir / "performance_{time:YYYY-MM-DD}.log"
        logger.add(
            perf_log,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            filter=lambda record: "duration" in record["message"].lower(),
            rotation="00:00",  # 每天午夜轮转
            retention="30 days",
        )

        if config.logging.enable_remote_logging and config.logging.remote_log_url:
            self._setup_remote_logging()

        logger.info("日志系统初始化完成")

    def _setup_remote_logging(self):
        try:
            from notifiers.logging import NotificationHandler

            params = {
                "username": "your_email@gmail.com",
                "password": "your_password",
                "to": "admin@example.com",
            }

            handler = NotificationHandler("gmail", defaults=params)

            logger.add(handler, level="ERROR", format="股票数据系统错误: {message}")

        except ImportError:
            logger.warning("未安装notifiers库，跳过远程日志配置")
        except Exception as e:
            logger.error(f"远程日志配置失败: {e}")

    def log_data_source_status(self, source_name: str, status: str, details: str = ""):
        logger.bind(source=source_name).info(f"数据源状态: {status} {details}")

    def log_download_progress(self, current: int, total: int, code: str = ""):
        progress = (current / total) * 100
        logger.info(f"下载进度: {current}/{total} ({progress:.1f}%) {code}")

    def log_performance(self, operation: str, duration: float):
        logger.info(f"操作性能 | {operation} | 耗时: {duration:.2f}秒")

    def get_logger(self):
        return logger


stock_logger = StockDataLogger()
logger = stock_logger.get_logger()
