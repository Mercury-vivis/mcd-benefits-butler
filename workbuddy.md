# workbuddy.md — WorkBuddy 会话上下文导出

> 本文档由 [WorkBuddy](https://www.workbuddy.cn) 智能体会话上下文整理导出，记录「麦麦权益管家」
> 从 McDonald's MCP 接入到参赛项目成型的**真实开发全过程**（2026-10-09，单日完成）。
> 本项目即基于 WorkBuddy + mcd-mcp-server 的真实协作产出，符合大赛"使用 WorkBuddy 开发"的奖励条件。

---

## 一、McDonald's MCP 接入过程

**用户指令**：接入 mcd-mcp-server（https://github.com/M-China/mcd-mcp-server）。

**WorkBuddy 执行**：
1. 读取仓库 README，确认接入三要素：Streamable HTTP 协议、地址 `https://mcp.mcd.cn`、鉴权头 `Authorization: Bearer <Token>`；
2. 对照 WorkBuddy 连接器文档确认 `mcp.json` 自定义连接器格式（`type: streamablehttp` + `headers`）；
3. 用户在麦当劳开放平台（open.mcd.cn/mcp）申请 Token 后提供；
4. WorkBuddy 写入 WorkBuddy 连接器配置并回读校验，随后用 curl 向 `https://mcp.mcd.cn` 发送 MCP `initialize` 请求做**真实连通性验证**：HTTP 200，返回 `serverInfo: {"name":"mcd-mcp","version":"1.0.0"}`，带 `tools` 能力；
5. 用户在 WorkBuddy「连接器」页对该服务点「信任」启用。

> 全程 Token 只写入本机配置文件与环境变量，未在对话中明文留存、未写入任何仓库文件。

## 二、能力盘点（tools/list 实测）

WorkBuddy 通过 `tools/list` 从服务端拉取**当前实际暴露的全部 35 个工具**（非 README 复述，服务端已迭代至 1.0.9+），按用途归类：

- 点餐/订单类 13 个（query-nearby-stores / delivery-* / query-meals / calculate-price / create-order / query-order / order-list / cancel-order / query-promotions / query-meal-assistance 等）
- 优惠券/积分类 6 个（query-store-coupons / query-my-coupons / available-coupons / auto-bind-coupons / query-my-account / query-survey-coupon）
- 商城积分兑换类 5 个（mall-points-products / mall-product-detail / mall-create-order / mall-order-list / mall-order-detail）
- 活动/抽奖/派对类 9 个（campaign-calendar / query-lottery-info / draw-lottery / query-my-prizes / query-party-* / party-order-create）
- 辅助类 2 个（now-time-info / list-nutrition-foods）

并实际调用 `campaign-calendar` 拉取了 2026 年 10 月营销活动日历（G-DRAGON/PEACEMINUSONE 联名、韩式风味系列、9.9 元早餐、麦金喜积分霸王餐等），验证了链路可用。

## 三、参赛方案论证（需求侧 + 评审侧 + 能力侧三方调研）

**用户指令**：除了从榜单推荐创意外，还需网络检索用户真实需求（小红书/抖音/美团等社区）、分析 GitHub 评审群体凭什么 Star、并评估智能体自身能力边界，多方论证后提方案。

**WorkBuddy 执行（全部真实网络检索 + 榜单分析）**：
1. **需求侧**：省钱优惠聚合最热但已红海（榜1 mcd-saver-strategist）；营养减脂次热但赛道拥挤（4 个竞品）且涉合规红线；**积分焦虑**（过期/不知换啥）与**抽奖霸王餐**需求真实且 GitHub 供给为零；满意度奖券（query-survey-coupon）为唯一性极强的零供给工具。
2. **评审侧**：大赛纯按 GitHub Star 排名、同一账号只算最高 Star 项目 ⇒ 必须做 1 个精品；跨圈传播力（有梗、有惊喜感）是低 Star 期突围关键。
3. **能力侧**：基于已验证可调的工具链路评估各方向难度。

**结论**：拍板「麦麦权益管家」整合型方案——满意度奖券挖宝 + 积分商城导购 + 活动抽奖聚合三大蓝海子能力，避开红海正面竞争。

## 四、项目搭建与实跑校准（本项目成型的关键过程）

**WorkBuddy 执行**：
1. 按官方参赛文件清单生成 README.md / MCP_INTEGRATION.md / mcp-config.example.json（仅 `${MCD_MCP_TOKEN}` 占位符）/ CONTEST_DECLARATION.md（原样照搬官方）/ SKILL.md / 源码骨架 / 冒烟测试；
2. **实跑探查**修正了三处关键假设（全部以真实返回为准）：
   - mcd-mcp 查询类工具统一返回「Markdown 包裹的完整 JSON」，真实数据在 `## Original Response` 标题后的 JSON 对象内 ⇒ 在客户端封装层统一增加结构化抽取，一处修复全局受益；
   - `mall-product-detail` 真实参数名为 `spuId`（非 productId）；`mall-create-order` 真实必填 `skuId` + `spuCategory`（无 productId/shopId）⇒ 按服务端 inputSchema 修正；
   - 严格遵循官方合规约束：商品 `note`/`spuLimit`/`partyPeople` 为纯展示字段，禁止提取数值做 AI 前置校验，所有"是否可兑换"以下单接口返回为准；
3. **真实数据验证**（开发者本人账号）：
   - `dig`：扫描历史订单，正确处理"无问卷=无遗漏券"场景；
   - `mall`：积分账户精确解析（可用 73 / 累计 968.6 / **已过期 870.6**），"积分过期作废"焦虑提示成功触发，24 件可兑商品按积分升序并标注可兑状态；
   - `activity`：活动日历 / 抽奖信息（麦麦积分抽奖，进行中）/ 可领券三段聚合正常。

## 五、结论

本项目从 McDonald's MCP 接入、35 工具盘点、参赛方案三方论证，到代码骨架生成、三处关键假设修正、真实账号数据验证，**全程在 WorkBuddy 中由用户与智能体协作完成**，是"真实使用 WorkBuddy + mcd-mcp-server 开发"的一手记录。
