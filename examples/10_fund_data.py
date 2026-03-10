"""
示例 10: 基金数据获取

演示如何获取基金数据：净值数据、基金信息。

支持的基金类型:
- 股票型基金
- 混合型基金
- 债券型基金
- 指数型基金 (ETF/LOF)
- 货币型基金
"""

import finshare as fs


def main():
    """运行基金数据获取示例"""

    fs.logger.info("=" * 60)
    fs.logger.info("finshare 基金数据获取示例")
    fs.logger.info("=" * 60)

    # 基金代码示例
    fund_codes = [
        "161039",  # 富国中证1000指数增强(LOF)A
        "000001",  # 平安财富宝货币A
        "110011",  # 易方达消费行业股票
    ]

    # 1. 获取基金净值数据
    fs.logger.info("\n=== 获取基金净值数据 ===")
    code = "161039"  # 富国中证1000指数增强

    try:
        # 获取最近90天的净值数据
        data = fs.get_fund_nav(
            code=code,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        if data and len(data) > 0:
            fs.logger.info(f"✓ 成功获取 {code} {len(data)} 条净值数据")
            fs.logger.info(f"  基金名称: {data[0].name}")

            # 计算涨跌幅
            first_nav = data[0].nav
            last_nav = data[-1].nav
            change = (last_nav - first_nav) / first_nav * 100

            fs.logger.info(f"  日期范围: {data[0].nav_date} 至 {data[-1].nav_date}")
            fs.logger.info(f"  期初净值: {first_nav:.4f}")
            fs.logger.info(f"  期末净值: {last_nav:.4f}")
            fs.logger.info(f"  年涨跌幅: {change:+.2f}%")

            # 打印最近5天的净值
            fs.logger.info("\n  最近5个交易日净值:")
            for item in data[-5:]:
                change_pct = item.change_pct if item.change_pct else 0
                fs.logger.info(
                    f"    {item.nav_date}: nav={item.nav:.4f}, change_pct={change_pct:+.2f}%"
                )
        else:
            fs.logger.warning(f"未获取到 {code} 的净值数据")

    except Exception as e:
        fs.logger.error(f"获取基金净值失败: {e}")

    # 2. 获取基金基本信息
    fs.logger.info("\n=== 获取基金基本信息 ===")

    try:
        info = fs.get_fund_info(code)

        if info:
            fs.logger.info(f"✓ {code} 基金信息:")
            for key, value in info.items():
                fs.logger.info(f"  {key}: {value}")
        else:
            fs.logger.warning("未获取到基金信息")

    except Exception as e:
        fs.logger.error(f"获取基金信息失败: {e}")

    # 3. 批量获取多只基金最新净值
    fs.logger.info("\n=== 批量获取多只基金净值 ===")

    for fund_code in fund_codes:
        try:
            # 获取最近30天的数据
            data = fs.get_fund_nav(
                code=fund_code,
                start_date="2024-12-01",
                end_date="2024-12-31"
            )

            if data and len(data) > 0:
                latest = data[-1]
                change_pct = latest.change_pct if latest.change_pct else 0

                fs.logger.info(
                    f"  {fund_code}: {latest.name[:20]:<20} "
                    f"nav={latest.nav:.4f} ({change_pct:+.2f}%)"
                )
            else:
                fs.logger.warning(f"  {fund_code}: 无数据")

        except Exception as e:
            fs.logger.error(f"获取 {fund_code} 净值失败: {e}")

    # 4. 提示
    fs.logger.info("\n" + "=" * 60)
    fs.logger.info("提示:")
    fs.logger.info("  - 基金代码格式: 161039, 000001 (6位数字)")
    fs.logger.info("  - 数据来源: EastMoney (天天基金)")
    fs.logger.info("  - 净值更新: 每个交易日收盘后更新")
    fs.logger.info("  - 常见基金代码:")
    fs.logger.info("    - 161039: 富国中证1000指数增强(LOF)A")
    fs.logger.info("    - 000001: 平安财富宝货币A")
    fs.logger.info("    - 110011: 易方达消费行业股票")


if __name__ == "__main__":
    main()
