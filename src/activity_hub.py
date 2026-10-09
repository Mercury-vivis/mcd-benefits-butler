"""子模块3 · 活动 / 抽奖日历聚合。

mcd-mcp 工具统一返回「Markdown 包裹的完整 JSON」，client._extract_text 已抽取：
- campaign-calendar / available-coupons：真实数据未以 Original Response JSON 暴露，
  回退为原始 Markdown 文本 ⇒ 清洗后透传展示（剥离 <img> 等终端无用的 HTML 标签）。
- query-lottery-info：含 Original Response JSON ⇒ 抽取为 dict，取 data 展示概要。
"""
import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcd_mcp_client import McdMcpClient, McdMcpError  # noqa: E402

SECTIONS = [
    ("campaignCalendar", "campaign-calendar", {}, "📅 当月营销活动日历"),
    ("lottery", "query-lottery-info", {}, "🎰 积分抽奖信息"),
    ("availableCoupons", "available-coupons", {}, "🎟️ 麦麦省可领券"),
]

_IMG_RE = re.compile(r"<img[^>]*>\s*", re.IGNORECASE)


def _clean_md(text):
    """透传前剥离 <img> 等展示噪音（终端与 LLM 消费场景无需图片 URL）。"""
    if not isinstance(text, str):
        return text
    return _IMG_RE.sub("", text)


def aggregate(client: McdMcpClient) -> dict:
    """聚合三段信息，返回 [{key, title, markdown, json(可选)}]。"""
    sections = []
    for key, tool, args, title in SECTIONS:
        try:
            raw = client.call_tool(tool, args)
        except McdMcpError as e:
            sections.append({
                "key": key, "title": title,
                "markdown": f"（获取失败：{e}）", "json": None,
            })
            continue
        if key == "lottery" and isinstance(raw, dict):
            sections.append({
                "key": key, "title": title,
                "markdown": "（抽奖活动结构化信息见下方概要；是否可参与以下单/抽奖接口返回为准）",
                "json": raw.get("data") or {},
            })
        else:
            md = _clean_md(raw) if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
            sections.append({"key": key, "title": title, "markdown": md, "json": None})
    return {"sections": sections}


def draw(client: McdMcpClient, activity_id: str = None) -> dict:
    """执行一次积分抽奖。"""
    try:
        return client.call_tool("draw-lottery", {"activityId": activity_id} if activity_id else {})
    except McdMcpError as e:
        return {"error": str(e)}


def claim_all(client: McdMcpClient) -> dict:
    """一键领取全部麦麦省券。"""
    try:
        return client.call_tool("auto-bind-coupons", {})
    except McdMcpError as e:
        return {"error": str(e)}
