---
name: mcd-benefits-butler
description: 麦当劳权益管家——基于官方 mcd-mcp-server，帮你挖回漏领的满意度奖券、精算积分商城兑换、聚合当月活动与抽奖日历。当用户提到"麦当劳漏领券/满意度奖券/问卷奖券/积分兑换/积分商城/麦麦省/霸王餐/积分抽奖/麦金喜/活动日历/麦当劳优惠/麦当劳权益"等意图时启用。
---

# 麦麦权益管家（McDonald's Benefits Butler）

一个基于**麦当劳中国官方 MCP**（`mcd-mcp-server`，地址 `https://mcp.mcd.cn`）的权益盘活工具。
核心叙事：**帮你把散落在各处的麦当劳权益一次性盘活，不再漏、不再废。**

## 前置条件

1. 已在 WorkBuddy「连接器」页接入并**信任启用** `mcd-mcp`（远程 Streamable HTTP，带 `Authorization: Bearer` 头）。
2. Token 由用户自行在 `https://open.mcd.cn/mcp` 申请，配置在工作区 `mcp.json`，Skill 不接触明文。
3. 本 Skill 仅调用官方已公开工具，不做任何逆向或越权。

## 三大子能力

### 子能力 1 · 满意度奖券挖宝 🕵️（最强记忆点）
- **触发词**："我有没有漏领的券 / 满意度奖券 / 问卷奖券 / 点完忘填问卷的免费券"
- **工具链**：`order-list` → 逐单 `query-survey-coupon`
- **输出**：扫描历史订单，列出"点完没填问卷、关联但可能过期的免费券"，给出可领清单与数量。
- **差异化**：该工具全榜目前 0 竞品，且具"找回被遗忘权益"的跨圈传播钩子。

### 子能力 2 · 积分商城导购 💎（蓝海）
- **触发词**："我积分能换啥 / 积分商城 / 积分兑换 / 积分快过期怎么办"
- **工具链**：`query-my-account` → `mall-points-products` → `mall-product-detail` → `mall-create-order`
- **输出**：读取积分余额，推荐性价比最高的兑换组合，支持一键下单（shopId=2）。

### 子能力 3 · 活动 / 抽奖日历聚合 📅（蓝海）
- **触发词**："这周麦当劳有啥活动 / 霸王餐 / 麦金喜抽奖 / 麦麦省领券 / 活动日历"
- **工具链**：`campaign-calendar` + `query-lottery-info` / `draw-lottery` + `available-coupons` / `auto-bind-coupons`
- **输出**：聚合当月活动、抽奖信息、可领券，生成"本周权益日程"，支持一键参与 / 领券。

## 调用约定（在 WorkBuddy 中）

- 优先直接调用已接入的 `mcd-mcp` 对应工具（连接器已信任），按上面工具链组织多轮调用。
- 如需批量 / 脚本化（如逐单扫描），可用仓库 `src/` 下的 Python 封装：
  - `src/mcd_mcp_client.py`：Streamable HTTP 客户端（initialize + tools/call + 限流退避）。
  - `src/dig_coupons.py` / `src/mall_advisor.py` / `src/activity_hub.py`：三个子模块。
  - `src/main.py dig|mall|activity`：命令行示例。

## 合规与免责（务必遵守）

- **不**将麦当劳与其他品牌做对比（活动规则合规红线）。
- 营养 / 健康相关表述一律标注"仅供参考，非专业建议"。
- 所有输出以麦当劳官方实时结果为准；餐品、价格、供应状态可能变动。
- 本 Skill 为大赛参赛作品，非麦当劳官方产品（详见 `CONTEST_DECLARATION.md`）。

## 项目仓库与源码

- 参赛仓库根目录含：`README.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`、`CONTEST_DECLARATION.md`（原样不可改）、`SKILL.md`、`src/`。
- 完整 MCP 工具映射与调用流程见 `MCP_INTEGRATION.md`。
