# finshare Tests

本目录包含 finshare 的测试用例。

## 测试结构

```
tests/
├── conftest.py           # pytest 配置和夹具
├── test_models.py        # 数据模型测试
├── test_sources.py       # 数据源测试
└── test_utils.py         # 工具函数测试
```

## 运行测试

### 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_models.py
pytest tests/test_utils.py
```

### 运行特定测试类

```bash
pytest tests/test_models.py::TestKLineData
```

### 显示详细输出

```bash
pytest -v
```

### 显示打印输出

```bash
pytest -s
```

### 生成覆盖率报告

```bash
pytest --cov=finshare --cov-report=html
```

然后在浏览器中打开 `htmlcov/index.html` 查看报告。

### 生成覆盖率报告（终端）

```bash
pytest --cov=finshare --cov-report=term-missing
```

## 测试标记

### 单元测试

```bash
pytest -m unit
```

### 跳过集成测试

```bash
pytest -m "not integration"
```

集成测试需要网络连接，在 CI 环境中可能需要跳过。

## 测试夹具

### sample_kline_data
生成示例 K线数据，包含 20 天的 OHLCV 数据。

```python
def test_example(sample_kline_data):
    assert len(sample_kline_data) == 20
```

### sample_stock_codes
提供示例股票代码列表。

```python
def test_example(sample_stock_codes):
    assert '000001.SZ' in sample_stock_codes
```

### mock_snapshot_data
提供模拟的快照数据。

```python
def test_example(mock_snapshot_data):
    assert mock_snapshot_data['code'] == '000001.SZ'
```

## 编写测试

### 测试命名规范

- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test_*`

### 测试示例

```python
import pytest
from finshare import get_data_manager

class TestDataManager:
    """测试数据管理器"""

    def test_get_manager(self):
        """测试获取管理器"""
        manager = get_data_manager()
        assert manager is not None

    def test_invalid_code(self):
        """测试无效代码"""
        manager = get_data_manager()
        with pytest.raises(ValueError):
            manager.get_kline('INVALID')
```

## 测试覆盖率目标

- **总体覆盖率**: > 80%
- **核心模块**: > 90%
  - models
  - utils
  - sources (基类和管理器)

## CI/CD 集成

测试会在以下情况自动运行：
- 每次 push 到 GitHub
- 每次创建 Pull Request
- 每次发布新版本

## 注意事项

1. **集成测试**
   - 标记为 `@pytest.mark.integration`
   - 需要网络连接
   - 可能较慢
   - CI 环境中可能跳过

2. **Mock 使用**
   - 对外部依赖使用 mock
   - 避免真实的网络请求
   - 提高测试速度和稳定性

3. **测试隔离**
   - 每个测试应该独立
   - 不依赖其他测试的结果
   - 使用夹具提供测试数据

## 贡献测试

欢迎贡献测试用例！请确保：

- 测试覆盖新功能
- 测试通过所有检查
- 遵循测试命名规范
- 添加必要的文档字符串

## 相关资源

- [pytest 文档](https://docs.pytest.org/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)
- [finshare 文档](https://finshare.readthedocs.io)
