# 麦麦权益管家 · McDonald's Benefits Butler

![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue) ![Powered by MCP](https://img.shields.io/badge/Powered%20by-MCP-blueviolet) ![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-success) ![McD Dev Contest 2026](https://img.shields.io/badge/McD%20Dev%20Contest-2026%20Entry-red)

[English](./README_EN.md) | 简体中文

> 一个基于**麦当劳官方 MCP 能力**（`mcd-mcp-server`）的 WorkBuddy Skill / 开源工具。
>
> **官方只在你买单那一刻提醒你一次，之后便再无人提。它帮你回头翻历史订单，把还来得及的评价券扫出来。**

---

## 🎯 先说清楚：它做什么，不做什么

麦当劳的微信小程序、官方 App、支付宝小程序，已经把**积分兑换、领券、抽奖**做得很完整（每月 8 号会员日、周一"麦麦省"、周六"麦金喜"等官方入口都很成熟）。这些事**用官方 App 就够了**，本项目不打算替代它们。

真正没人管的是这一件：

- **"用餐后评价 → 领券"这个机制，官方只在你买单那一刻提醒一次**，入口是三类被动触发：支付后的推送、桌贴/小票上的二维码、公众号回复；
- **你没点、没扫、忘了，它就再也不会出现**——官方没有任何入口会回头告诉你"你有哪些订单还没评价、还来得及领券"。

麦麦权益管家就补这一件事：**扫描历史订单，把尚未评价、且奖励券仍可领取的订单挑出来，列成待办提醒你。**

> 依据：麦当劳中国官网新闻《顾客反馈移动平台上线》（2017-01-23）与《5元换购券！分享用餐体验就能GET》证实中国区确有"用餐后评价→发放换购券"机制，入口为上述三类被动触发；在官方渠道与公开检索中，我们未见任何"回溯历史未评价订单"的入口。这正是本项目的立足点。

---

## ✨ 能力

### 1. 用餐评价券扫描 🕵️（唯一主打 · 官方未见对应入口）
逐单扫描历史订单，挑出**尚未完成评价、奖励券仍可领取**的订单，一次性给出待办清单。

### 2. 积分盘点与兑换建议 💎（官方已有，我们补"排序 + 临期提醒"）
官方小程序 / App 内已有积分商城。本工具读取积分账户，按所需积分升序排列可兑商品并标注当前能否兑换，同时把**已过期 / 临期风险**摆到明处，专治"不知换啥、眼看过期"。

### 3. 活动与抽奖一屏聚合 📅（官方已有，我们补"聚合"）
官方 App 独占"周一麦麦省""周六麦金喜"等活动。本工具把当月活动日历、积分抽奖信息、可领券聚合到一屏，省去在多个入口来回翻。

---

## ⚖️ 与官方渠道的关系（先看这张表）

| 事项 | 官方 App / 微信小程序 | 本工具 |
|---|---|---|
| 点餐、支付、常规领券 | ✅ 完整，体验最好 | ❌ 不做，也不打算做 |
| 积分查询与兑换 | ✅ 已有积分商城 | 🔸 排序建议 + 临期提醒 |
| 活动 / 抽奖参与 | ✅ 官方独占入口 | 🔸 一屏聚合展示 |
| **回溯"哪些订单还没评价"** | ❌ 未见官方入口 | ✅ **本项目唯一主打** |

**能力边界（不夸大）**：评价券有领取窗口，错过后大概率不可补领——本工具的价值是**在仍来得及的时候把待办挑出来**，不会变出已经失效的券；且**并非每笔订单都附带评价邀请**，扫描结果为"本次未发现待评价订单"属正常情况。

---

## 🌟 零安装：用 WorkBuddy 一键接入（推荐小白）

不想装 Python、配环境变量？**用 WorkBuddy 零安装直接玩**：

1. 打开 WorkBuddy → 左侧「连接器」页，找到 **mcd-mcp**（麦当劳官方 MCP）；
2. 点「信任」启用，按提示填你的麦当劳 MCP Token（申请：https://open.mcd.cn/mcp）；
3. 把本仓库作为 Skill 接入（见 [`SKILL.md`](./SKILL.md)），或直接对我说：
   > "用麦麦权益管家帮我扫一下，有没有还没评价的订单"

命令行、Token 管理、官方工具调用全部自动跑，**无需任何代码基础**。
想自己改代码 / 本地跑，见 [`docs/小白安装指南.md`](./docs/小白安装指南.md) 与下方「快速开始」。

---

## 🚀 快速开始

```bash
# 1. 配置 Token（仅环境变量，绝不入库）
export MCD_MCP_TOKEN="你的麦当劳MCP Token"   # 申请地址：https://open.mcd.cn/mcp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行示例 CLI
python src/main.py dig        # 用餐评价券扫描
python src/main.py mall       # 积分盘点与兑换建议
python src/main.py activity   # 活动 / 抽奖一屏聚合
```

**WorkBuddy 用户**：将本仓库作为 Skill 接入（见 `SKILL.md`），MCP 配置参考 `mcp-config.example.json`，在连接器页对 `mcd-mcp` 点「信任」启用。

---

## 📸 演示截图（真实运行输出）
- ![评价券扫描](docs/dig-demo.png)
- ![积分盘点](docs/mall-demo.png)
- ![活动聚合](docs/activity-demo.png)

---

## 🧩 架构

```
用户输入
   │
   ▼
main.py（命令行路由）
   │
   ▼
mcd_mcp_client.py（MCP Streamable HTTP 封装：initialize + tools/call + session）
   │
   ├─ dig_coupons.py      （用餐评价券扫描 · 主打）
   ├─ mall_advisor.py     （积分盘点与兑换建议）
   └─ activity_hub.py     （活动 / 抽奖聚合）
   │
   ▼
mcd-mcp-server（麦当劳官方，35 个工具，本 Skill 使用其中 8+ 个）
```

各子模块与官方工具的映射、调用流程、业务价值，详见 [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md)。

---

## ⚠️ 声明

本项目为「麦当劳程序员节创意开发大赛」参赛作品，由参赛者独立开发，**非麦当劳官方产品**。项目输出仅供参考，不构成医疗、营养或其他专业建议；餐品信息、价格、权益规则及供应状态，**以麦当劳官方渠道（官方 App / 微信小程序 / 支付宝小程序）的实时结果为准**。详见 [`CONTEST_DECLARATION.md`](./CONTEST_DECLARATION.md)。

---

## 🏆 参赛信息

- 赛事：麦当劳程序员节创意开发大赛
- 基础能力：[`mcd-mcp-server`](https://github.com/M-China/mcd-mcp-server)（麦当劳中国官方远程 MCP）
- 形式：开源 Skill，按 GitHub 公开 Star 排名领奖
