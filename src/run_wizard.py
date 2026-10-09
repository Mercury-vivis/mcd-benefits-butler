#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦权益管家 — 小白交互向导（双击 run.bat 启动）。

职责：引导不懂命令行的小白，用交互菜单完成三大能力调用。
- 自动把 Windows 控制台切成 UTF-8，避免中文乱码；
- Token 仅在本次运行的内存环境变量里，绝不写入任何文件；
- 复用 main.py 的打印函数，保证输出与 CLI 一致。
"""
import sys
import os

# Windows 控制台 UTF-8 输出，避免中文方块
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json  # noqa: E402
from mcd_mcp_client import McdMcpClient, McdMcpError  # noqa: E402
import dig_coupons  # noqa: E402
import mall_advisor  # noqa: E402
import activity_hub  # noqa: E402
from main import _print_dig, _print_mall, _print_activity  # noqa: E402


def _div():
    print("\n" + "=" * 56)


def _ensure_token():
    tok = os.environ.get("MCD_MCP_TOKEN")
    if tok:
        return tok
    print("=" * 56)
    print("首次使用需要先填入你的麦当劳 MCP Token。")
    print("它只存在于本次运行的临时环境里，关闭窗口即消失，不会写入任何文件。")
    print("申请地址：https://open.mcd.cn/mcp")
    print("=" * 56)
    val = input("请粘贴 Token 后回车：").strip()
    if not val:
        print("[提示] 未输入 Token，程序将因鉴权失败而退出。")
        return None
    os.environ["MCD_MCP_TOKEN"] = val
    return val


def _menu():
    """生成器：每次产出用户选择，遇到退出返回。"""
    while True:
        _div()
        print("麦麦权益管家 · 交互菜单")
        print("  1) 满意度奖券挖宝  —— 查你漏领的免费券")
        print("  2) 积分商城导购    —— 查积分 + 推荐最值兑换")
        print("  3) 活动 / 抽奖日历 —— 看本周有啥优惠 / 抽奖")
        print("  4) 执行一次积分抽奖 —— ⚠️ 会消耗积分，谨慎")
        print("  5) 一键领取麦麦省券")
        print("  0) 退出")
        _div()
        try:
            choice = input("请输入数字选择：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            return
        if choice == "0":
            print("再见 👋")
            return
        yield choice


def main():
    tok = _ensure_token()
    if not tok:
        input("按回车退出…")
        return
    try:
        client = McdMcpClient()
        info = client.initialize()
        si = info.get("serverInfo", {})
        print(f"[OK] 已连接 {si.get('name')} v{si.get('version')}")
    except McdMcpError as e:
        print(f"[ERROR] 连接失败：{e}")
        input("按回车退出…")
        return

    for choice in _menu():
        try:
            if choice == "1":
                _print_dig(dig_coupons.dig(client))
            elif choice == "2":
                _print_mall(mall_advisor.advise(client))
            elif choice == "3":
                _print_activity(activity_hub.aggregate(client))
            elif choice == "4":
                print("[谨慎] 此操作会消耗你的积分。输入 yes 继续，其他任意键取消：")
                if input().strip().lower() == "yes":
                    print(json.dumps(activity_hub.draw(client),
                                     ensure_ascii=False, indent=2))
                else:
                    print("已取消，未消耗积分。")
            elif choice == "5":
                print(json.dumps(activity_hub.claim_all(client),
                                 ensure_ascii=False, indent=2))
            else:
                print("请输入 0-5 之间的数字。")
        except McdMcpError as e:
            print(f"[ERROR] {e}")
        input("\n--- 按回车返回菜单 ---")

    input("按回车退出…")


if __name__ == "__main__":
    main()
