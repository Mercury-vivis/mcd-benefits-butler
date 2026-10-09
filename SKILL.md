---
name: mcd-benefits-butler
description: 麦当劳权益管家——基于官方 mcd-mcp-server，扫描历史订单找出「尚未评价、奖励券仍可领取」的订单（官方渠道未见此类回溯入口）；另做积分盘点与兑换建议、活动抽奖聚合。当用户提到"麦当劳漏领券/还没评价的订单/用餐评价/满意度问卷奖券/积分兑换/积分商城/麦麦省/霸王餐/积分抽奖/麦金喜/活动日历/麦当劳优惠/麦当劳权益"等意图时启用。
---

# 麦麦权益管家（McDonald's Benefits Butler）

一个基于**麦当劳中国官方 MCP**（`mcd-mcp-server`，地址 `https://mcp.mcd.cn`）的权益提醒工具。

核心叙事：**官方只在你买单那一刻提醒你一次，之后便再无人提。本 Skill 帮你回头翻历史订单，把还来得及的评价券扫出来。**

## 前置条件

1. 已在 WorkBuddy「连接器」页接入并**信任启用** `mcd-mcp`（远程 Streamable HTTP，带 `Authorization: Bearer` 头）。
2. Token 由用户自行在 `https://open.mcd.cn/mcp` 申请，配置在工作区 `mcp.json`，Skill 不接触明文。
3. 本 Skill 仅调用官方已公开工具，不做任何逆向或越权。

## 定位边界（回答前先自我确认）

官方微信小程序 / App / 支付宝小程序**已完整覆盖**点餐、常规领券、积分兑换、活动抽奖（每月 8 号会员日、周一"麦麦省"、周六"麦金喜"等）。**不宣称本工具替代或优于官方渠道。**

唯一的主打差异是：**官方未见提供"回溯历史未评价订单"的入口**——评价邀请属事后被动触发（支付后推送 / 桌贴·小票二维码 / 公众号回复），错过即不再出现。

## 子能力

### 子能力 1 · 用餐评价券扫描 🕵️（唯一主打）
- **触发词**："有没有没评价的订单 / 我有没有漏领的券 / 满意度奖券 / 问卷奖券 / 点完忘评价的免费券"
- **工具链**：`order-list` → 逐单 `query-survey-coupon`
- **输出**：列出"尚未评价、奖励券仍可领取"的订单待办清单；无结果时如实说明"本次未发现待评价订单"。
- **边界（不可夸大）**：并非每笔订单都附带评价邀请；评价券有领取窗口，错过后大概率不可补领——本能力的价值是"在仍来得及的时候提醒"，**不是找回已失效的券**。

### 子能力 2 · 积分盘点与兑换建议 💎（官方已有，我们补排序与临期提醒）
- **触发词**："我积分能换啥 / 积分商城 / 积分兑换 / 积分快过期怎么办"
- **工具链**：`query-my-account` → `mall-points-products` → `mall-product-detail` → `mall-create-order`
- **输出**：读取积分余额（可用 / 累计 / 已过期），商品按所需积分升序排列并标注当前能否兑换，把过期风险摆在明处。
- **参数与合规**：参数一律以 `tools/list` 的 inputSchema 为准——`mall-create-order` 实测必填 `skuId` + `spuCategory`（"1"虚拟 / "2"实体），**不存在 shopId 参数**；`mall-product-detail` 入参为 `spuId`（非 productId）。是否可兑换**以官方下单接口返回为准**，官方明令禁止对 `note` / `spuLimit` / `partyPeople` 等展示字段做 AI 前置校验。

### 子能力 3 · 活动 / 抽奖一屏聚合 📅（官方已有，我们补聚合）
- **触发词**："这周麦当劳有啥活动 / 霸王餐 / 麦金喜抽奖 / 麦麦省领券 / 活动日历"
- **工具链**：`campaign-calendar` + `query-lottery-info` / `draw-lottery` + `available-coupons` / `auto-bind-coupons`
- **输出**：聚合当月活动、抽奖信息、可领券，生成"本周权益日程"。

## 调用约定（在 WorkBuddy 中）

- 优先直接调用已接入的 `mcd-mcp` 对应工具（连接器已信任），按上面工具链组织多轮调用。
- 如需批量 / 脚本化（如逐单扫描），可用仓库 `src/` 下的 Python 封装：
  - `src/mcd_mcp_client.py`：Streamable HTTP 客户端（initialize + tools/call + 限流退避）。
  - `src/dig_coupons.py` / `src/mall_advisor.py` / `src/activity_hub.py`：三个子模块。
  - `src/main.py dig|mall|activity`：命令行示例。
- **返回格式提醒**：多数查询工具返回的是**"Markdown 包裹的 JSON"**，真实数据在 `## Original Response` 标题后的 JSON 对象内；`campaign-calendar` / `available-coupons` 则回退为纯 Markdown 文本。

## 合规与免责（务必遵守）

- **不**将麦当劳与其他品牌做对比（活动规则合规红线）。
- 营养 / 健康相关表述一律标注"仅供参考，非专业建议"。
- 所有输出以麦当劳官方实时结果为准；餐品、价格、权益规则、供应状态可能变动。
- 不承诺"找回已过期的券"、不宣称"官方做不到的事情我们能做到"。
- 本 Skill 为大赛参赛作品，非麦当劳官方产品（详见 `CONTEST_DECLARATION.md`）。

## 项目仓库与源码

- 参赛仓库根目录含：`README.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`、`CONTEST_DECLARATION.md`（原样不可改）、`SKILL.md`、`src/`。
- 完整 MCP 工具映射与调用流程见 `MCP_INTEGRATION.md`。
