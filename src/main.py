#!/usr/bin/env python3
"""麦麦权益管家 — 示例命令行入口。

用法：
    export MCD_MCP_TOKEN="你的Token"
    python src/main.py dig        # 满意度奖券挖宝（查询，安全）
    python src/main.py mall       # 积分商城导购（查询，安全）
    python src/main.py activity   # 活动 / 抽奖日历聚合（查询，安全）
    python src/main.py draw       # 执行一次积分抽奖（⚠️ 消耗积分）
    python src/main.py claim      # 一键领取全部麦麦省券
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcd_mcp_client import McdMcpClient, McdMcpError  # noqa: E402
import dig_coupons  # noqa: E402
import mall_advisor  # noqa: E402
import activity_hub  # noqa: E402


def _print_activity(result: dict):
    """activity 工具返回 Markdown，按段友好展示（不转义 JSON）。"""
    for s in result.get("sections", []):
        print(f"\n{'=' * 60}\n{s.get('title', '')}\n{'=' * 60}\n")
        print(s.get("markdown", ""))
        j = s.get("json")
        if j and isinstance(j, dict) and s.get("key") == "lottery":
            data = j
            dd = data.get("drawDecision", {}) or {}
            print("\n[抽奖概要] 名称: {} | 状态: {} | 单次消耗: {} 积分 | 可用积分: {} | 资格: {}".format(
                data.get("activityName"), data.get("activityStatusText"),
                data.get("drawPoint"), data.get("availablePoint"),
                dd.get("resourceEligible")))
            print("  activityCode: {} | 奖品数: {}".format(
                data.get("activityCode"), len(data.get("prizes") or [])))


def _print_dig(result: dict):
    if "error" in result:
        print("[ERROR] %s" % result["error"])
        return
    for m in result.get("messages", []):
        print(m)
    found = result.get("found", [])
    if not found:
        print("\n本次未发现遗漏未核销奖券。")
        return
    print("\n💎 发现 %d 张遗漏未核销奖券：" % len(found))
    for f in found:
        c = f.get("coupon", {})
        print("  - 订单 %s（%s @ %s，%s 元）" % (
            f.get("orderId"), f.get("storeName"), f.get("createTime"), f.get("amount")))
        print("    券：%s | 状态：%s | 有效期至：%s | 剩余核销：%s" % (
            c.get("title"), c.get("redeemStatus"),
            c.get("tradeEndTime"), c.get("availableCount")))


def _print_mall(result: dict):
    if "error" in result:
        print("[ERROR] %s" % result["error"])
        return
    acc = result.get("account") or {}
    insight = result.get("insight") or {}
    if isinstance(acc, dict):
        print("💰 积分账户（%s）：可用 %s，累计 %s，已过期 %s" % (
            acc.get("currency"),
            acc.get("availablePointRaw") or acc.get("availablePoint"),
            acc.get("accumulativePointRaw") or acc.get("accumulativePoint"),
            acc.get("expiredPointRaw") or acc.get("expiredPoint")))
    if insight.get("tip"):
        print("📌 %s" % insight["tip"])
    rec = result.get("recommendation") or []
    print("\n🛍️ 可积分兑换商品（按所需积分升序，共 %d 件）：" % len(rec))
    for x in rec:
        flag = "✅可兑" if x.get("redeemableNow") else "⚠️积分不足需攒"
        print("  - %s：%s 积分（%s）[%s] %s" % (
            x.get("spuName"), x.get("point"), x.get("catName"),
            flag, x.get("selling") or ""))
    print("\n（提示：是否可兑换以下单接口返回为准；积分不够的商品可通过点餐攒积分。）")


def main():
    p = argparse.ArgumentParser(description="麦麦权益管家 CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dig", help="满意度奖券挖宝（查询）")
    sub.add_parser("mall", help="积分商城导购（查询）")
    sub.add_parser("activity", help="活动/抽奖日历聚合（查询）")
    sub.add_parser("draw", help="执行一次积分抽奖（⚠️ 消耗积分）")
    sub.add_parser("claim", help="一键领取全部麦麦省券")
    args = p.parse_args()

    try:
        client = McdMcpClient()
        info = client.initialize()
        si = info.get("serverInfo", {})
        print(f"[OK] 已连接 {si.get('name')} v{si.get('version')}")

        if args.cmd == "dig":
            _print_dig(dig_coupons.dig(client))
        elif args.cmd == "mall":
            _print_mall(mall_advisor.advise(client))
        elif args.cmd == "activity":
            _print_activity(activity_hub.aggregate(client))
        elif args.cmd == "draw":
            print(json.dumps(activity_hub.draw(client), ensure_ascii=False, indent=2))
        elif args.cmd == "claim":
            print(json.dumps(activity_hub.claim_all(client), ensure_ascii=False, indent=2))
        else:
            p.error("未知命令")
            return
    except McdMcpError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
