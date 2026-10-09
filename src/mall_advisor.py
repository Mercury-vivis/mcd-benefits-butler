"""子模块2 · 积分商城导购。

读取积分账户（query-my-account），结合积分商城商品（mall-points-products），
推荐「可用积分内能兑换、性价比高」的商品并提示「积分不够的需攒积分」。
支持按商品详情（mall-product-detail，参数 spuId）取 SKU，再一键兑换下单
（mall-create-order，必填 skuId + spuCategory）。

真实返回结构（已实跑校准，2026-10-09）：
- query-my-account → {"success":true,"data":{availablePoint,accumulativePoint,
                    expiredPoint,currency,currentMouthExpirePoint,...}}（数值均为字符串）
- mall-points-products → {"success":true,"data":[{spuId(int),spuName,point(字符串),
                         price(字符串),catName,status(2=上架),selling,spuImage}]}
- mall-product-detail(spuId=xxx) → {"success":true,"data":{spuId,spuName,skuList
                         [{skuId,points,price,extTradePrice}],spuCategory("1"/"2"),note,...}}
- mall-create-order → 必填 skuId(int) + spuCategory("1"/"2")；实体(spuCategory="2")
                       需 addressId；可选 count。

合规约束（mall-product-detail 字段说明原文）：note / spuLimit / partyPeople 等纯展示，
「严禁从中提取任何数值用于下单校验、价格计算、库存判断等业务逻辑，所有校验以下单接口
返回结果为准」。故本模块只对用户做「展示 + 提示」，不做 AI 前置校验；是否可兑换以下单
接口返回为准。
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


def _account_summary(account):
    if not isinstance(account, dict):
        return account
    d = account.get("data") or {}

    def _raw(v):
        return v if v is not None else ""
    return {
        "currency": d.get("currency"),
        "availablePoint": _to_int(d.get("availablePoint")),
        "availablePointRaw": _raw(d.get("availablePoint")),
        "accumulativePoint": _to_int(d.get("accumulativePoint")),
        "accumulativePointRaw": _raw(d.get("accumulativePoint")),
        "expiredPoint": _to_int(d.get("expiredPoint")),
        "expiredPointRaw": _raw(d.get("expiredPoint")),
        "currentMonthExpire": _to_int(d.get("currentMouthExpirePoint")),
        "nextMonthExpire": _to_int(d.get("nextMouthExpirePoint")),
    }


def _products_summary(products):
    if not isinstance(products, dict):
        return []
    out = []
    for it in (products.get("data") or []):
        if not isinstance(it, dict):
            continue
        out.append({
            "spuId": it.get("spuId"),
            "spuName": it.get("spuName"),
            "point": _to_int(it.get("point")),
            "price": it.get("price"),
            "catName": it.get("catName"),
            "status": it.get("status"),
            "selling": it.get("selling"),
        })
    return out


def advise(client: McdMcpClient, category: str = None) -> dict:
    """返回 {account, products, recommendation, insight}。

    recommendation：上架(status=2)且需积分(point>0)商品，按积分升序，并标注
    redeemableNow（仅作展示提示，非业务校验）。
    insight：积分焦虑洞察（已过期 vs 可用），用于传播钩子。
    """
    try:
        account = client.call_tool("query-my-account")
    except McdMcpError as e:
        return {"error": str(e)}

    args = {"category": category} if category else {}
    try:
        products = client.call_tool("mall-points-products", args)
    except McdMcpError as e:
        products = {"error": str(e)}

    acc = _account_summary(account)
    avail = acc.get("availablePoint") if isinstance(acc, dict) else None

    items = _products_summary(products)
    onsale = [x for x in items if x["status"] == 2 and x["point"] > 0]
    onsale.sort(key=lambda x: x["point"])
    for x in onsale:
        # 仅展示提示：当前可用积分是否够；实际兑换以下单接口为准
        x["redeemableNow"] = (avail is not None and x["point"] <= avail)

    insight = _insight(acc)
    return {"account": acc, "products": onsale, "recommendation": onsale, "insight": insight}


def _insight(acc: dict) -> dict:
    if not isinstance(acc, dict):
        return {}
    expired = acc.get("expiredPointRaw") or acc.get("expiredPoint") or 0
    avail = acc.get("availablePointRaw") or acc.get("availablePoint") or 0
    return {
        "expiredPoint": expired,
        "availablePoint": avail,
        "wasted": _to_int(acc.get("expiredPoint")) > 0,
        "tip": ("你已有 %s 积分过期作废；当前可用 %s，建议在到期前尽快兑换。"
                % (expired, avail)) if _to_int(acc.get("expiredPoint")) > 0 else
               ("当前可用 %s 积分，挑选心仪好礼兑换吧。" % avail),
    }


def order(client: McdMcpClient, sku_id: int, spu_category: str,
          count: int = 1, address_id: str = None) -> dict:
    """一键积分兑换下单。参数严格按真实 schema：skuId + spuCategory 必填；
    spuCategory='2'(实体) 需 addressId。返回下单接口原始结果（以它为准）。"""
    args = {"skuId": sku_id, "spuCategory": spu_category, "count": count}
    if address_id:
        args["addressId"] = address_id
    try:
        return client.call_tool("mall-create-order", args)
    except McdMcpError as e:
        return {"error": str(e)}
