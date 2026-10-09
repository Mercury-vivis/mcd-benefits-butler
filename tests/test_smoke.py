#!/usr/bin/env python3
"""冒烟测试：用本地已配置的 Token 验证客户端可连通官方 MCP。

仅本地验证用；从 ~/.workbuddy/mcp.json 读取 Token，绝不回显明文。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from mcd_mcp_client import McdMcpClient, McdMcpError  # noqa: E402

CFG = os.path.expanduser("~/.workbuddy/mcp.json")


def load_token():
    with open(CFG, encoding="utf-8") as f:
        data = json.load(f)
    auth = data["mcpServers"]["mcd-mcp"]["headers"]["Authorization"]
    return auth.split(" ", 1)[1] if " " in auth else auth


def main():
    token = load_token()
    client = McdMcpClient(token=token)
    info = client.initialize()
    si = info.get("serverInfo", {})
    print(f"[OK] initialize -> {si.get('name')} v{si.get('version')}")
    r = client.call_tool("campaign-calendar")
    if isinstance(r, dict):
        print(f"[OK] tools/call campaign-calendar -> keys={list(r.keys())[:8]}")
    else:
        print(f"[OK] tools/call campaign-calendar -> type={type(r).__name__}")
    print("[SMOKE PASS]")


if __name__ == "__main__":
    try:
        main()
    except McdMcpError as e:
        print(f"[SMOKE FAIL] {e}")
        sys.exit(1)
