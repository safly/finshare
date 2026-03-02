# Contributing to finshare

感谢你对 finshare 的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug

如果你发现了 bug，请在 [GitHub Issues](https://github.com/meepo-quant/finshare/issues) 创建一个 issue，并包含：

- 清晰的标题和描述
- 重现步骤
- 预期行为和实际行为
- 你的环境信息（Python 版本、操作系统等）
- 如果可能，提供最小可重现示例

### 提出新功能

如果你有新功能的想法：

1. 先在 Issues 中搜索，确保没有重复
2. 创建一个新的 issue，描述你的想法
3. 等待维护者的反馈

### 提交代码

1. **Fork 仓库**

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编写代码**
   - 遵循项目的代码风格
   - 添加必要的测试
   - 更新文档

4. **运行测试**
   ```bash
   pytest
   ```

5. **代码格式化**
   ```bash
   black finshare tests
   flake8 finshare tests
   ```

6. **提交代码**
   ```bash
   git commit -m "feat: add your feature"
   ```

7. **推送到 GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **创建 Pull Request**

## 代码规范

### Python 代码风格

- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 使用 [Flake8](https://flake8.pycqa.org/) 进行代码检查
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: add new data source
fix: correct data parsing
docs: update installation guide
```

### 测试要求

- 所有新功能必须包含测试
- 测试覆盖率应保持在 80% 以上
- 确保所有测试通过

### 文档要求

- 为公共 API 添加 docstring
- 更新相关文档
- 如果添加新功能，在 README 中说明

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/meepo-quant/finshare.git
cd finshare

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black finshare tests
flake8 finshare tests
```

## 项目范围

finshare 专注于**数据获取**功能，以下内容不在项目范围内：

- ❌ 策略回测
- ❌ 实盘交易
- ❌ 策略开发
- ❌ 因子分析

如果你需要这些功能，请访问 [米波量化平台](https://meepoquant.com)。

## 行为准则

- 尊重所有贡献者
- 保持友好和专业
- 接受建设性的批评
- 关注对项目最有利的事情

## 问题？

如有任何问题，请：

- 查看 [文档](https://finshare.readthedocs.io)
- 在 [Issues](https://github.com/meepo-quant/finshare/issues) 中提问
- 访问 [米波社区](https://meepoquant.com/community)

感谢你的贡献！🎉
