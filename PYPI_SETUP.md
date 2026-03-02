# PyPI 自动发布设置指南

## 📝 步骤 1: 获取 PyPI API Token

1. 访问 https://pypi.org/account/register/ 注册账号（如果还没有）
2. 登录后访问 https://pypi.org/manage/account/token/
3. 点击 "Add API token"
4. 填写信息：
   - **Token name**: `finshare-github-actions`
   - **Scope**: 选择 "Entire account"（首次发布）或 "Project: finshare"（已发布后）
5. 复制生成的 token（格式：`pypi-AgEIcHlwaS5vcmc...`）

⚠️ **重要**: Token 只显示一次，请立即保存！

---

## 📝 步骤 2: 在 GitHub 中添加 Secret

1. 访问仓库设置: https://github.com/finvfamily/finshare/settings/secrets/actions
2. 点击 "New repository secret"
3. 填写信息：
   - **Name**: `PYPI_API_TOKEN`
   - **Secret**: 粘贴你的 PyPI token
4. 点击 "Add secret"

---

## 📝 步骤 3: 推送 GitHub Actions 配置

```bash
git add .github/workflows/
git commit -m "ci: add GitHub Actions for PyPI publishing and tests"
git push origin main
```

---

## 📝 步骤 4: 触发发布

### 方式一：通过 Release 自动触发（推荐）

每次创建新的 Release 时会自动发布到 PyPI：

```bash
gh release create v0.1.1 --title "v0.1.1" --notes "Bug fixes"
```

### 方式二：手动触发

1. 访问 Actions 页面: https://github.com/finvfamily/finshare/actions
2. 选择 "Publish to PyPI" workflow
3. 点击 "Run workflow"
4. 选择分支（main）
5. 点击 "Run workflow"

---

## 📝 步骤 5: 验证发布

发布成功后：

1. 访问 PyPI 查看: https://pypi.org/project/meepo-finshare/
2. 测试安装:
   ```bash
   pip install meepo-finshare
   python -c "import finshare; print(finshare.__version__)"
   ```

---

## 🔍 工作流说明

### publish.yml
- **触发条件**: Release 发布或手动触发
- **功能**: 构建包并发布到 PyPI
- **需要**: PYPI_API_TOKEN secret

### tests.yml
- **触发条件**: Push 到 main 或 Pull Request
- **功能**: 运行测试和代码检查
- **Python 版本**: 3.8, 3.9, 3.10, 3.11

---

## ✅ 检查清单

- [ ] 获取 PyPI API token
- [ ] 在 GitHub 添加 PYPI_API_TOKEN secret
- [ ] 推送 GitHub Actions 配置
- [ ] 触发发布（Release 或手动）
- [ ] 验证 PyPI 上的包

---

## 🎉 完成！

配置完成后，每次创建 Release 都会自动发布到 PyPI！
