# McDonald's Benefits Butler · 麦麦权益管家

[English](./README_EN.md) | 简体中文

![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue) ![Powered by MCP](https://img.shields.io/badge/Powered%20by-MCP-blueviolet) ![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-success) ![McD Dev Contest 2026](https://img.shields.io/badge/McD%20Dev%20Contest-2026%20Entry-red)

> An open-source WorkBuddy Skill / CLI tool built on the **official McDonald's China MCP server** (`mcd-mcp-server`). It digs out all the McDonald's perks you own but keep forgetting — expired survey coupons, idle loyalty points, weekly lotteries — and puts them back in your hands.

---

## 🎯 The Problem

Inside the McDonald's app, you actually own a bunch of "perks" — but they are scattered across different entry points and easy to forget:

- Forgot to fill the satisfaction survey after ordering → **the coupon linked to it quietly expires**
- Sitting on a pile of loyalty points, not knowing what's worth redeeming before they expire
- Weekly lotteries / coupon drops / limited campaigns, but who can keep track of the calendar?

McDonald's Benefits Butler uses **official MCP tools** to dig up, calculate, and schedule all of these automatically. It does exactly one thing: **make sure no McDonald's perk of yours goes missed or wasted**.

## ✨ Three Capabilities

### 1. Survey Coupon Treasure Hunt 🕵️
Scans your order history and queries each order for the survey-linked coupon you never claimed — lists **all the free-item coupons you left on the table**.

> The hook: "You actually missed X free burgers." The surprise of recovering forgotten perks travels well beyond developer circles.

### 2. Points Mall Advisor 💎
Reads your points account, ranks every redeemable item, and recommends the **best-value redemption combo** — with one-click ordering. Built for "points anxiety" (what to redeem? they expire soon!).

### 3. Campaign / Lottery Calendar 📅
Aggregates the monthly campaign calendar, points lottery (e.g. the weekly "Points Free Meal" jackpot), and claimable coupons — so you always know **which day brings which deal, and join with one click**.

## 🚀 Quick Start

```bash
# 1. Configure your token (env var only — never committed)
export MCD_MCP_TOKEN="your McDonald's MCP token"   # apply at: https://open.mcd.cn/mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the sample CLI
python src/main.py dig        # survey coupon treasure hunt
python src/main.py mall       # points mall advisor
python src/main.py activity   # campaign / lottery calendar
```

**WorkBuddy users**: add this repo as a Skill (see `SKILL.md`); MCP config reference in `mcp-config.example.json`; enable `mcd-mcp` from the connector page.

## 📸 Demo Screenshots (real output)

- ![Treasure hunt](docs/dig-demo.png)
- ![Points advisor](docs/mall-demo.png)
- ![Campaign calendar](docs/activity-demo.png)

## 🧩 Architecture

```
User input
   │
   ▼
main.py (CLI routing)
   │
   ▼
mcd_mcp_client.py (MCP Streamable HTTP wrapper: initialize + tools/call + session)
   │
   ├─ dig_coupons.py      (survey coupon treasure hunt)
   ├─ mall_advisor.py     (points mall advisor)
   └─ activity_hub.py     (campaign / lottery calendar)
   │
   ▼
mcd-mcp-server (official McDonald's China remote MCP, 35 tools; this Skill uses 8+)
```

Tool mapping, call flows and business value: see [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md).

## ⚠️ Disclaimer

This project is an entry to the McDonald's Developer Innovation Challenge, independently developed by the contestant — **not an official McDonald's product**. All output is for reference only and does not constitute medical, nutritional or other professional advice. Menu items, prices and availability are subject to real-time results from official McDonald's channels. See [`CONTEST_DECLARATION.md`](./CONTEST_DECLARATION.md).

## 🏆 Contest

- Event: McDonald's Developer Innovation Challenge (2026)
- Foundation: [`mcd-mcp-server`](https://github.com/M-China/mcd-mcp-server) (official McDonald's China remote MCP)
- Format: open-source Skill; winners ranked by public GitHub Stars
