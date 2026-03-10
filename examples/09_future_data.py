"""
示例 9: 期货数据获取

演示如何获取期货数据：历史K线、实时行情。

支持的期货品种:
- 股指期货: IF (沪深300), IH (上证50), IC (中证500)
- 金属期货: CU (沪铜), AL (沪铝), AU (沪金), AG (沪银)
- 能源化工: SC (原油), RU (橡胶), TA (PTA)
- 农产品: M (豆粕), Y (豆油), P (棕榈油)
"""

import finshare as fs


def main():
    """运行期货数据获取示例"""

    fs.logger.info("=" * 60)
    fs.logger.info("finshare 期货数据获取示例")
    fs.logger.info("=" * 60)

    # 期货代码示例
    # 使用连续合约 (如 cu0, IF0) 获取主力连续合约数据
    future_codes = [
        "cu0",   # 沪铜连续
        "au0",   # 沪金连续
        "ru0",   # 橡胶连续
    ]

    # 1. 获取期货历史K线
    fs.logger.info("\n=== 获取期货历史K线 ===")
    code = "cu0"  # 沪铜连续合约

    try:
        # 获取最近30天的数据
        data = fs.get_future_kline(
            code=code,
            start_date="2024-06-01",
            end_date="2024-07-17"
        )

        if data and len(data) > 0:
            fs.logger.info(f"✓ 成功获取 {code} {len(data)} 条日K线数据")

            # 计算涨跌幅
            first_price = data[0].close_price
            last_price = data[-1].close_price
            change = (last_price - first_price) / first_price * 100

            fs.logger.info(f"  日期范围: {data[0].trade_date} 至 {data[-1].trade_date}")
            fs.logger.info(f"  起始价: {first_price:.2f}")
            fs.logger.info(f"  结束价: {last_price:.2f}")
            fs.logger.info(f"  涨跌幅: {change:+.2f}%")

            # 统计
            fs.logger.info(f"  最高价: {max(d.high_price for d in data):.2f}")
            fs.logger.info(f"  最低价: {min(d.low_price for d in data):.2f}")
            fs.logger.info(f"  成交量: {sum(d.volume for d in data):,.0f} 手")
        else:
            fs.logger.warning(f"未获取到 {code} 的历史数据")

    except Exception as e:
        fs.logger.error(f"获取期货历史数据失败: {e}")

    # 2. 获取期货实时快照
    fs.logger.info("\n=== 获取期货实时快照 ===")

    try:
        # 获取单只期货快照
        snapshot = fs.get_future_snapshot("cu0")

        if snapshot:
            fs.logger.info(f"✓ {snapshot.code} 实时行情:")
            fs.logger.info(f"  最新价: {snapshot.last_price}")
            fs.logger.info(f"  涨跌额: {snapshot.change}")
            fs.logger.info(f"  涨跌幅: {snapshot.change_pct}%")
            fs.logger.info(f"  持仓量: {snapshot.open_interest}")
            fs.logger.info(f"  成交量: {snapshot.volume}")
        else:
            fs.logger.warning("未获取到期货快照数据")

    except Exception as e:
        fs.logger.error(f"获取期货快照失败: {e}")

    # 3. 批量获取期货快照
    fs.logger.info("\n=== 批量获取期货快照 ===")

    try:
        results = fs.get_batch_future_snapshots(future_codes)
        fs.logger.info(f"成功获取 {len(results)} 只期货的快照")

        fs.logger.info("\n期货实时行情:")
        fs.logger.info("-" * 60)
        fs.logger.info(f"{'代码':<12} {'最新价':<12} {'涨跌幅':<12} {'持仓量':<15}")
        fs.logger.info("-" * 60)

        for code, snapshot in results.items():
            change_pct = snapshot.change_pct if snapshot.change_pct else 0
            fs.logger.info(
                f"{code:<12} {snapshot.last_price:<12.2f} {change_pct:>+11.2f}% {snapshot.open_interest:>15,.0f}"
            )

    except Exception as e:
        fs.logger.error(f"批量获取期货快照失败: {e}")

    # 4. 提示
    fs.logger.info("\n" + "=" * 60)
    fs.logger.info("提示:")
    fs.logger.info("  - 期货代码格式: cu0 (连续合约), cu2409 (具体合约)")
    fs.logger.info("  - 连续合约: cu0 (当月), cu1 (下月), cu2 (下下月)")
    fs.logger.info("  - 股指期货: IF0 (沪深300), IH0 (上证50), IC0 (中证500)")
    fs.logger.info("  - 数据来源: Sina (历史), EastMoney (备用)")
    fs.logger.info("  - 注意: Sina期货数据可能略有延迟")


if __name__ == "__main__":
    main()
