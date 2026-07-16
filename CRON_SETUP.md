# Phoenix-Live CRON 设置指南

> 适用: Windows 10/11 + Python 3.13 + 本地 Chrome + PhoenixLive dashboard 9:00/16:00 自动抓取

## 📋 换机要做的 3 步

### 1️⃣ 安装依赖 (Python + Playwright + Chrome)

```powershell
# Python 3.13 (Windows installer from python.org)
# 安装时勾选 "Add Python to PATH"

# 安装依赖
pip install playwright requests beautifulsoup4 lxml

# 安装 Playwright 浏览器 (如果用 Playwright, 必须)
python -m playwright install chromium

# 验证 Chrome 路径
Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe"
# 应该返回 True
```

### 2️⃣ 配置 .env (GitHub Token)

```powershell
# 创建 .env 在 D:\MINIMAX\phoenix-live\.env
# 内容:
PHOENIX_GH_TOKEN=ghp_your_token_here

# Token 必须是 Fine-grained PAT, 权限:
#   - Contents: Read and Write
#   - Expiration: No expiration
# 申请: https://github.com/settings/tokens
```

### 3️⃣ 配置 Windows 计划任务 (9:00 + 16:00)

```powershell
# 创建 9:00 任务
schtasks /Create /SC DAILY /TN "PhoenixLive_DailyCrawler" `
  /TR "D:\MINIMAX\phoenix-live\run_daily.bat" `
  /ST 09:00 /F

# 创建 16:00 任务
schtasks /Create /SC DAILY /TN "PhoenixLive_DailyCrawler_16" `
  /TR "D:\MINIMAX\phoenix-live\run_daily.bat" `
  /ST 16:00 /F

# 验证
schtasks /Query /TN "PhoenixLive_DailyCrawler"
schtasks /Query /TN "PhoenixLive_DailyCrawler_16"
```

## 🔧 链路说明

```
Windows 计划任务 (9:00/16:00)
  ↓ schtasks 触发
run_daily.bat
  ↓ 调 powershell
run_daily.ps1
  ↓ 调 python
crawler\_safe_crawl.py
  ↓ Playwright + 13 BD 关键词 + 3 retry
  ↓ baseline 双重保护 (30 绝对最低 / 0.7 相对)
  ↓ 写 data/latest.json + data/history.json
  ↓ 自动 deploy 到 GitHub (PHOENIX_GH_TOKEN)
  ↓ CF Pages webhook rebuild (5-10 分钟)
```

## ⚠️ 关键文件

| 文件 | 作用 | 是否在 git |
|------|------|-----------|
| `run_daily.bat` | schtasks 调用的入口 (log 落盘) | ✅ 已加入 git (V2.9.17-P2.2) |
| `run_daily.ps1` | 调 python 脚本 (token 加载 + Python PATH) | ✅ 已加入 git (V2.9.17-P2.2) |
| `crawler/_safe_crawl.py` | 抓取 + baseline 保护 + history + deploy | ✅ 已在 git (V2.9.17-P1.5) |
| `.env` | GitHub Token (敏感, 不入 git) | ❌ .gitignore |
| `data/latest.json` | 实时价格池 (部署到 CF Pages) | ✅ 已在 git |
| `data/history.json` | 7 日价格历史 | ✅ 已在 git |

## 🐛 故障排查

### 1. 抓取失败 (0 SKU)
- **症状**: `data\logs\phoenix_crawl.log` 看到 "0 SKU (attempt 1-3)"
- **原因**: Daraz.com.bd 反爬严重, SSL EOF
- **解决**: 自动 baseline 保护 (130+ SKU baseline 不会丢)

### 2. deploy 失败
- **症状**: `_safe_crawl.py` 跑到 == deploy == 但没有 [OK]
- **原因**: SSL EOF 偶发 (GitHub API 限速)
- **解决**: `_safe_crawl.py` 已 retry 3 次; 失败可手动跑 `python deploy.py data`

### 3. schtasks 没跑
- **症状**: `phoenix-daily-verify` (mavis cron) 报告 latest.json 90 分钟前
- **检查**: 
  ```powershell
  schtasks /Query /TN "PhoenixLive_DailyCrawler" /V
  # 看 "上次运行时间" 和 "上次结果"
  ```
- **手动触发**: 右键 → "运行"

### 4. CF Pages 没更新
- **症状**: GitHub 上文件已更新, dashboard 还是旧的
- **原因**: CF Pages webhook 5-10 分钟延迟, 偶尔失败
- **解决**: 手动去 https://dash.cloudflare.com → Pages → phoenix-live → Deployments → Retry

## 🔄 更新流程 (日常)

| 时机 | 操作 |
|------|------|
| 9:00 | schtasks 自动跑 _safe_crawl.py |
| 9:30 | `phoenix-daily-verify` cron 检查 (mavis agent) |
| 16:00 | schtasks 自动跑 _safe_crawl.py |
| 16:30 | `phoenix-daily-verify` cron 检查 |
| 用户主动改 dashboard | 手动 `python deploy.py html` |

## 📊 部署历史 (最近)

| 版本 | sha | 说明 |
|------|-----|------|
| V2.9.17-P2.1 | `e9fca103` (index.html) | 视觉全检 188 处颜色修复 |
| V2.9.17-P1.6 | cron 切换 | `run_daily.ps1` 改用 `_safe_crawl.py` |
| V2.9.17-P1.5 | `e104f3e1` | `_safe_crawl.py` 安全网抓取脚本 |
| V2.9.17-P0 | `1915b0aa` | 数据失真修复 (190+141 baseline 恢复) |
| V2.9.17 | `009513aa` | 4 国市场聚焦 + 简化 (TH/PH/MY/VN 删除) |
| V2.9.16 | `ca54614b` (bd/matrix) | 产品矩阵聚焦产品 + 视觉优化 |

---

*V2.9.17-P2.2 创建 (2026-07-16)*
*作者: Mavis (PHOENIX-LIVE assistant)*
