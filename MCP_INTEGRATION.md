# MCP 集成说明 · MCP_INTEGRATION.md

本文档说明「麦麦权益管家」如何接入并使用麦当劳官方 MCP 能力，供评委与开发者核对。

---

## 一、接入的 Server

| 项 | 值 |
|---|---|
| 名称 | `mcd-mcp-server`（麦当劳中国官方） |
| 协议 | Streamable HTTP（远程托管，无需本地起进程） |
| 地址 | `https://mcp.mcd.cn` |
| 鉴权 | 请求头 `Authorization: Bearer <MCD_MCP_TOKEN>` |
| 能力规模 | 服务端当前暴露 **35 个工具**（版本 1.0.9+） |
| 本 Skill 使用 | 其中 **11 个**（覆盖三大子能力） |

> 注：本 Skill 仅声明并使用了官方已公开的 MCP 工具，未对麦当劳系统进行任何逆向或越权访问。

---

## 二、鉴权与配置

- 配置文件示例见 [`mcp-config.example.json`](./mcp-config.example.json)。
- 仅使用 `${MCD_MCP_TOKEN}` **环境变量占位符**，仓库内**不含任何真实 Token / 密钥**（符合《参赛声明》信息安全条款）。
- Token 申请：https://open.mcd.cn/mcp （登录 → 控制台 → 激活 → 申请 Token）。
- 限流：每 Token 600 次 / 分钟，超限返回 429。

---

## 三、使用的工具与调用流程

### 子模块 1 · 满意度奖券挖宝（dig_coupons）
| 顺序 | 工具 | 用途 |
|---|---|---|
| 1 | `order-list` | 拉取历史订单（非商城） |
| 2 | `query-survey-coupon` | 按订单查 CSAT 满意度答卷 + 关联奖券（逐单调用） |

**业务闭环**：`order-list` 拿全部历史单 → 对每单调 `query-survey-coupon` → 汇总"未领取 / 临期"的关联奖券 → 输出可领清单。
**差异化**：该工具全榜目前 0 人使用，且具备"惊喜感"传播钩子。

### 子模块 2 · 积分商城导购（mall_advisor）
| 顺序 | 工具 | 用途 | 关键参数（已实跑校准） |
|---|---|---|---|
| 1 | `query-my-account` | 查积分账户（可用 / 累计 / 已过期等，数值均为字符串） | — |
| 2 | `mall-points-products` | 积分可兑换商品列表（status=2 上架、point>0 为纯积分品） | 可选 `category` |
| 3 | `mall-product-detail` | 商品详情（skuList 内含下单必填 `skuId`、spuCategory） | **`spuId`（int）** |
| 4 | `mall-create-order` | 积分兑换下单 | **必填 `skuId`(int) + `spuCategory`("1"虚拟/"2"实体)；实体需 `addressId`；可选 `count`** |

**业务闭环**：读积分余额 → 拉可兑换商品 → 按积分升序推荐 → 提示"积分不足需攒"（遵循官方约束，仅展示、不做 AI 前置校验）→ 取商品详情 `skuId` 一键下单。
**合规**：`mall-product-detail` 的 `note` / `spuLimit` / `partyPeople` 字段官方明确"纯展示，严禁提取数值用于下单校验、价格计算、库存判断"，本模块严格遵循，所有"是否可兑换"以下单接口返回为准。

### 子模块 3 · 活动 / 抽奖日历聚合（activity_hub）
| 顺序 | 工具 | 用途 |
|---|---|---|
| 1 | `campaign-calendar` | 当月营销活动日历（已实测可调通） |
| 2 | `query-lottery-info` | 积分抽奖活动信息 |
| 3 | `draw-lottery` | 执行一次积分抽奖 |
| 4 | `available-coupons` | 麦麦省可领券列表 |
| 5 | `auto-bind-coupons` | 一键领取全部麦麦省券 |

**业务闭环**：聚合当月活动 + 抽奖信息 + 可领券 → 生成"本周权益日程" → 支持一键参与 / 领券。

---

## 四、通用调用流程

```
1. POST / initialize
   body: {jsonrpc, id, method:"initialize", params:{protocolVersion, capabilities, clientInfo}}
   → 解析 Mcp-Session-Id（部分实现需在后续请求回传）

2. POST / tools/call
   headers: Authorization: Bearer <TOKEN>, (Mcp-Session-Id)
   body: {jsonrpc, id, method:"tools/call", params:{name:<tool>, arguments:{...}}}
   → result.content[0].text 统一为 **「Markdown 包裹的完整 JSON」**：前端是字段说明
     （Response Structure），真实数据在 `## Original Response` 标题后的一个完整 JSON 对象内，
     形如 {"success":true,"code":200,"data":{...}}。
   - 含 Original Response JSON 的工具（order-list / query-my-account / mall-points-products /
     mall-product-detail / mall-order-list / query-survey-coupon / query-lottery-info 等）：
     抽取该 JSON 即得结构化 dict（业务数据在 `data` 字段内）。
   - 未暴露 Original Response JSON 的工具（campaign-calendar / available-coupons）：
     回退为原始 Markdown 文本，直接透传展示（本身即人友好格式）。

3. 业务层：`client._extract_text` 已统一完成上述抽取——返回 dict（结构化）或 str（Markdown）。
   业务代码按类型分支：结构化 dict 直接取 `data`；Markdown 文本直接展示。
```

请求头固定：`Content-Type: application/json`、`Accept: application/json, text/event-stream`。

---

## 五、业务价值映射

| 子模块 | 解决的真实痛点 | 供给侧竞争 |
|---|---|---|
| 满意度奖券挖宝 | "点完忘了填问卷，免费券白白过期" | **蓝海（0 竞品）** |
| 积分商城导购 | "积分焦虑：不知换啥、快过期" | **蓝海（0 竞品）** |
| 活动 / 抽奖聚合 | "活动信息散、记不住哪天有啥" | **蓝海（0 竞品）** |

> 刻意避开已在榜单拥挤的"省钱聚合""营养减脂"方向，切入需求真实、供给为零的"权益盘活"真空带。

---

## 六、错误处理

- Token 缺失 / 无效 → 明确提示申请地址，不输出任何凭证。
- `429` 限流 → 指数退避重试（最多 3 次）。
- 工具返回空 / 无权限 → 友好提示（如"暂无可挖奖券"），不抛未处理异常。
- 所有网络调用设置超时（默认 20s），避免挂死。
