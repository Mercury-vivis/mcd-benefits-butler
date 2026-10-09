# McDonald's Benefits Butler · 麦麦权益管家

English | [简体中文](./README.md)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue) ![Powered by MCP](https://img.shields.io/badge/Powered%20by-MCP-blueviolet) ![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-success) ![McD Dev Contest 2026](https://img.shields.io/badge/McD%20Dev%20Contest-2026%20Entry-red)

> An open-source WorkBuddy Skill / CLI tool built on the **official McDonald's China MCP server** (`mcd-mcp-server`).
>
> **The official app reminds you once, right when you pay — and never again. This tool looks back through your order history and flags the survey rewards you can still claim.**

---

## 🎯 What it does — and what it deliberately doesn't

McDonald's WeChat mini-program, official app and Alipay mini-program already handle **points redemption, coupon claims and lotteries** very well (monthly Member Day on the 8th, "Monday Savings", the Saturday lottery, and more). For those things, **the official app is enough** — this project does not try to replace it.

What nobody handles is this:

- **The "rate your visit → get a coupon" flow is offered to you exactly once**, at the moment you pay, through three passive triggers: a push notification after payment, a QR code on the table sticker or receipt, or replying in the official WeChat account;
- **Miss the tap, miss the scan, forget it — and it never comes back.** No official entry point will ever tell you afterwards "these orders were never rated, and the reward is still claimable".

McDonald's Benefits Butler covers exactly this one gap: **it scans your order history and lists the orders that are still unrated with a reward you can still claim.**

> Sources: McDonald's China official newsroom posts *Mobile Customer Feedback Platform Launches* (2017-01-23) and *Share Your Experience, Get a 5-Yuan Exchange Coupon* confirm that China has this "rate → coupon" mechanic, entered through the three passive triggers above. Across official channels and public search we found **no** entry point letting a user look back at unrated past orders. That gap is this project's reason to exist.

---

## ✨ Capabilities

### 1. Unrated-order reward scan 🕵️ (the one real differentiator)
Scans your order history and flags orders that are **still unrated with a reward coupon you can still claim**, giving you a single to-do list.

### 2. Points snapshot & redemption advice 💎 (official app already does this — we add sorting + expiry warnings)
The official mini-program / app already has a points mall. This tool reads your points account, lists redeemable items sorted by points required, marks what you can redeem right now, and puts **already-expired / expiring-soon** balances front and centre.

### 3. Campaign & lottery roll-up 📅 (official app already does this — we aggregate)
"Monday Savings" and the Saturday lottery live inside the official app. This tool rolls up the monthly campaign calendar, lottery details and claimable coupons into one screen.

---

## ⚖️ How this relates to official channels (read this first)

| Task | Official app / mini-program | This tool |
|---|---|---|
| Ordering, payment, regular coupons | ✅ Complete, best experience | ❌ Not done, not planned |
| Points inquiry & redemption | ✅ Points mall exists | 🔸 Sorting + expiry reminders |
| Campaign / lottery participation | ✅ Official-only entries | 🔸 Aggregated into one view |
| **Looking back at unrated orders** | ❌ No official entry found | ✅ **The single core feature** |

**Limits of what this does (no overclaiming):** reward coupons have a claim window; once it passes, they most likely cannot be recovered. The value here is **flagging the ones you can still act on** — it does not conjure back coupons that already lapsed. Also, **not every order carries a rating invitation**, so "no unrated orders found this run" is a perfectly normal result.

---

## 🚀 Quick Start

```bash
# 1. Configure your token (env var only — never committed)
export MCD_MCP_TOKEN="your McDonald's MCP token"   # apply at: https://open.mcd.cn/mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the sample CLI
python src/main.py dig        # unrated-order reward scan
python src/main.py mall       # points snapshot & advice
python src/main.py activity   # campaign / lottery roll-up
```

**WorkBuddy users**: add this repo as a Skill (see `SKILL.md`); MCP config reference in `mcp-config.example.json`; enable `mcd-mcp` from the connector page.

## 📸 Demo Screenshots (real output)

- ![Unrated-order scan](docs/dig-demo.png)
- ![Points snapshot](docs/mall-demo.png)
- ![Campaign roll-up](docs/activity-demo.png)

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
   ├─ dig_coupons.py      (unrated-order reward scan · core)
   ├─ mall_advisor.py     (points snapshot & advice)
   └─ activity_hub.py     (campaign / lottery roll-up)
   │
   ▼
mcd-mcp-server (official McDonald's China remote MCP, 35 tools; this Skill uses 8+)
```

Tool mapping, call flows and business value: see [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md).

## ⚠️ Disclaimer

This project is an entry to the McDonald's Developer Innovation Challenge, independently developed by the contestant — **not an official McDonald's product**. All output is for reference only and does not constitute medical, nutritional or other professional advice. Menu items, prices, benefit rules and availability are **subject to the real-time results of official McDonald's channels (official app / WeChat mini-program / Alipay mini-program)**. See [`CONTEST_DECLARATION.md`](./CONTEST_DECLARATION.md).

## 🏆 Contest

- Event: McDonald's Developer Innovation Challenge (2026)
- Foundation: [`mcd-mcp-server`](https://github.com/M-China/mcd-mcp-server) (official McDonald's China remote MCP)
- Format: open-source Skill; winners ranked by public GitHub Stars
