"""
示例 2: 批量获取数据

演示如何批量获取多只股票的数据。
"""

from finshare import get_data_manager, logger


def main():
    """运行批量数据获取示例"""

    logger.info("=" * 50)
    logger.info("finshare 批量数据获取示例")
    logger.info("=" * 50)

    # 1. 获取数据管理器
    manager = get_data_manager()

    # 2. 定义股票列表（只需6位代码）
    symbols = [
        "000001",  # 平安银行
        "000002",  # 万科A
        "600000",  # 浦发银行
        "600036",  # 招商银行
    ]

    logger.info(f"\n批量获取 {len(symbols)} 只股票的数据...")

    # 3. 批量获取 K线数据
    results = {}
    for symbol in symbols:
        try:
            logger.info(f"\n正在获取 {symbol}...")
            data = manager.get_historical_data(code=symbol, start="2024-01-01", end="2024-01-31")

            if data is not None and len(data) > 0:
                results[symbol] = data
                logger.info(f"✓ {symbol}: {len(data)} 条数据")
            else:
                logger.warning(f"✗ {symbol}: 未获取到数据")

        except Exception as e:
            logger.error(f"✗ {symbol}: {e}")

    # 4. 统计结果
    logger.info("\n" + "=" * 50)
    logger.info(f"成功获取 {len(results)}/{len(symbols)} 只股票的数据")

    # 5. 数据分析示例
    if results:
        logger.info("\n数据分析:")
        for symbol, data in results.items():
            change = (data["close_price"].iloc[-1] - data["close_price"].iloc[0]) / data["close_price"].iloc[0] * 100
            logger.info(f"  {symbol}: 涨跌幅 {change:+.2f}%")

    # 6. 提示
    logger.info("\n💡 提示:")
    logger.info("  - 获取数据后，可以使用 pandas 进行分析")
    logger.info("  - 需要策略回测？访问: https://meepoquant.com")


if __name__ == "__main__":
    main()
