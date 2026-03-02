"""
完整测试脚本 - 测试各类证券数据获取

测试范围：
- 股票（深圳、上海）
- ETF
- LOF
"""

from finshare import get_data_manager, logger
from datetime import datetime, timedelta


def test_data_fetch():
    """测试数据获取功能"""

    # 测试证券列表（包含股票、ETF、LOF）
    test_securities = [
        # 深圳股票
        ("000001", "平安银行", "股票"),
        ("000002", "万科A", "股票"),
        ("000858", "五粮液", "股票"),

        # 上海股票
        ("600000", "浦发银行", "股票"),
        ("600036", "招商银行", "股票"),
        ("601318", "中国平安", "股票"),

        # ETF
        ("159941", "纳指ETF", "ETF"),
        ("510300", "沪深300ETF", "ETF"),
        ("512880", "证券ETF", "ETF"),

        # LOF
        ("163402", "兴全趋势", "LOF"),
    ]

    logger.info("=" * 80)
    logger.info("finshare 完整功能测试")
    logger.info("=" * 80)

    # 初始化数据管理器
    logger.info("\n初始化数据管理器...")
    manager = get_data_manager()

    # 设置测试日期范围（最近1个月）
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    logger.info(f"\n测试日期范围: {start_date} 至 {end_date}")
    logger.info(f"测试证券数量: {len(test_securities)}")

    # 统计结果
    results = {
        "historical_success": [],
        "historical_failed": [],
        "snapshot_success": [],
        "snapshot_failed": [],
    }

    # 测试每个证券
    for code, name, sec_type in test_securities:
        logger.info("\n" + "-" * 80)
        logger.info(f"测试: {code} - {name} ({sec_type})")
        logger.info("-" * 80)

        # 1. 测试历史数据获取
        logger.info(f"\n[1/2] 获取历史K线数据...")
        try:
            data = manager.get_historical_data(
                code=code,
                start=start_date,
                end=end_date,
                adjust="qfq"
            )

            if data is not None and len(data) > 0:
                logger.info(f"✓ 历史数据获取成功: {len(data)} 条")
                logger.info(f"  数据列: {list(data.columns)}")
                logger.info(f"  日期范围: {data.iloc[0]['trade_date']} 至 {data.iloc[-1]['trade_date']}")
                logger.info(f"  价格范围: {data['close_price'].min():.2f} - {data['close_price'].max():.2f}")
                results["historical_success"].append((code, name, sec_type))
            else:
                logger.warning(f"✗ 历史数据获取失败: 未获取到数据")
                results["historical_failed"].append((code, name, sec_type))

        except Exception as e:
            logger.error(f"✗ 历史数据获取异常: {e}")
            results["historical_failed"].append((code, name, sec_type))

        # 2. 测试快照数据获取
        logger.info(f"\n[2/2] 获取实时快照数据...")
        try:
            snapshot = manager.get_snapshot_data(code)

            if snapshot:
                logger.info(f"✓ 快照数据获取成功")
                logger.info(f"  代码: {snapshot.code}")
                logger.info(f"  最新价: {snapshot.last_price}")
                logger.info(f"  成交量: {snapshot.volume}")
                logger.info(f"  成交额: {snapshot.amount}")
                logger.info(f"  数据源: {snapshot.data_source}")
                results["snapshot_success"].append((code, name, sec_type))
            else:
                logger.warning(f"✗ 快照数据获取失败: 未获取到数据")
                results["snapshot_failed"].append((code, name, sec_type))

        except Exception as e:
            logger.error(f"✗ 快照数据获取异常: {e}")
            results["snapshot_failed"].append((code, name, sec_type))

    # 输出测试总结
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)

    total = len(test_securities)

    logger.info(f"\n历史数据获取:")
    logger.info(f"  成功: {len(results['historical_success'])}/{total} ({len(results['historical_success'])/total*100:.1f}%)")
    logger.info(f"  失败: {len(results['historical_failed'])}/{total}")

    if results['historical_failed']:
        logger.info(f"\n  失败列表:")
        for code, name, sec_type in results['historical_failed']:
            logger.info(f"    - {code} {name} ({sec_type})")

    logger.info(f"\n快照数据获取:")
    logger.info(f"  成功: {len(results['snapshot_success'])}/{total} ({len(results['snapshot_success'])/total*100:.1f}%)")
    logger.info(f"  失败: {len(results['snapshot_failed'])}/{total}")

    if results['snapshot_failed']:
        logger.info(f"\n  失败列表:")
        for code, name, sec_type in results['snapshot_failed']:
            logger.info(f"    - {code} {name} ({sec_type})")

    # 按类型统计
    logger.info(f"\n按类型统计:")
    for sec_type in ["股票", "ETF", "LOF"]:
        type_securities = [s for s in test_securities if s[2] == sec_type]
        type_hist_success = [s for s in results['historical_success'] if s[2] == sec_type]
        type_snap_success = [s for s in results['snapshot_success'] if s[2] == sec_type]

        logger.info(f"\n  {sec_type}:")
        logger.info(f"    历史数据: {len(type_hist_success)}/{len(type_securities)} 成功")
        logger.info(f"    快照数据: {len(type_snap_success)}/{len(type_securities)} 成功")

    # 数据源统计
    logger.info(f"\n数据源统计:")
    source_stats = manager.get_source_stats()
    for source_name, stats in source_stats.items():
        status = "✓ 可用" if stats['available'] else "✗ 不可用"
        logger.info(f"  {source_name}: {status}")
        if not stats['available'] and stats['remaining_hours'] > 0:
            logger.info(f"    冷却剩余: {stats['remaining_hours']:.1f} 小时")
            logger.info(f"    失败原因: {stats['error_msg']}")

    logger.info("\n" + "=" * 80)
    logger.info("测试完成")
    logger.info("=" * 80)

    # 返回测试结果
    return results


if __name__ == "__main__":
    test_data_fetch()
