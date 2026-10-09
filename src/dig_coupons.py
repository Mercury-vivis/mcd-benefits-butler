"""子模块1 · 满意度奖券挖宝。

扫描历史订单（order-list），逐单查询「点完餐是否填了满意度问卷、关联奖券是否还没核销」
（query-survey-coupon），把可能被遗忘、即将过期的免费券一次性挖出来。

真实返回结构（已实跑校准，2026-10-09）：
- order-list  → {"success":true,"data":{"list":[{orderId,storeName,createTime,
               orderStatus,realTotalAmount,orderProductList}]}}
- query-survey-coupon → {"success":false,"code":499,"message":"该订单无匹配的答卷"}
                        （无问卷 ⇒ 无券，属正常跳过）
                      → {"success":true,"data":{coupon_title,coupon_redeem_status
                        ("可核销"/"已核销"),coupon_trade_end_time,
                        coupon_available_redeem_count,...}}

mcd-mcp 工具统一返回「Markdown 包裹的完整 JSON」，client 已抽取为 dict。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcd_mcp_client import McdMcpClient, McdMcpError  # noqa: E402


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def dig(client: McdMcpClient, page_size: int = 20) -> dict:
    """返回 {scanned, leakCount, found:[...], messages:[...]}。

    found 仅收录「已填问卷 ⇒ 有券」且「coupon_redeem_status == 可核销」的遗漏奖券。
    无答卷 / 已核销 / 接口异常均不计入 found（属正常或需人工核对）。
    """
    messages = []
    try:
        orders = client.call_tool("order-list", {"pageSize": page_size})
    except McdMcpError as e:
        return {"error": str(e)}

    order_list = []
    if isinstance(orders, dict):
        order_list = (orders.get("data") or {}).get("list") or []
    elif isinstance(orders, list):
        order_list = orders
    messages.append("已扫描历史订单 %d 笔" % len(order_list))

    found = []
    for o in order_list:
        oid = o.get("orderId")
        if not oid:
            continue
        try:
            r = client.call_tool("query-survey-coupon", {"orderId": oid})
        except McdMcpError as e:
            messages.append("订单 %s 查询异常：%s" % (oid, e))
            continue
        if not isinstance(r, dict) or not r.get("success"):
            # 无匹配答卷 / 无券 ⇒ 正常跳过（如 code 499）
            continue
        data = r.get("data") or {}
        status = data.get("coupon_redeem_status")
        if status != "可核销":
            # 已核销或状态不清 ⇒ 非遗漏，跳过
            continue
        found.append({
            "orderId": oid,
            "storeName": o.get("storeName"),
            "createTime": o.get("createTime"),
            "amount": o.get("realTotalAmount"),
            "coupon": {
                "title": data.get("coupon_title"),
                "redeemStatus": status,
                "tradeEndTime": data.get("coupon_trade_end_time"),
                "availableCount": data.get("coupon_available_redeem_count"),
            },
        })

    leak_count = len(found)
    if leak_count == 0:
        messages.append("未发现遗漏未核销的满意度奖券（可能订单均未填问卷，或奖券已核销）")
    else:
        messages.append("⚠️ 发现 %d 张遗漏未核销的免费券，请尽快在到期前核销！" % leak_count)
    return {"scanned": len(order_list), "leakCount": leak_count,
            "found": found, "messages": messages}
