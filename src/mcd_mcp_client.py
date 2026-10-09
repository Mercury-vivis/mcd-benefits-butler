"""麦当劳官方 MCP（Streamable HTTP）客户端封装。

仅使用标准库，零第三方依赖。Token 只从环境变量 MCD_MCP_TOKEN 读取，
绝不出现任何真实凭证（符合《参赛声明》信息安全条款）。
"""
import os
import re
import json
import time
import urllib.request
import urllib.error

ENDPOINT = "https://mcp.mcd.cn"
PROTOCOL_VERSION = "2024-11-05"


class McdMcpError(Exception):
    """MCP 调用相关的统一异常。"""


class McdMcpClient:
    def __init__(self, token=None, endpoint=ENDPOINT, timeout=20):
        self.token = token or os.environ.get("MCD_MCP_TOKEN")
        if not self.token:
            raise McdMcpError(
                "缺少 MCD_MCP_TOKEN：请设置环境变量。申请地址 https://open.mcd.cn/mcp"
            )
        self.endpoint = endpoint
        self.timeout = timeout
        self.session_id = None
        self._server_info = None

    # ---- 底层 HTTP ----
    def _headers(self):
        h = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            h["Mcp-Session-Id"] = self.session_id
        return h

    @staticmethod
    def _parse_body(raw: str):
        """兼容 application/json 与 text/event-stream 两种返回。"""
        raw = (raw or "").strip()
        if not raw:
            raise McdMcpError("MCP 返回空响应")
        if raw.startswith("{"):
            return json.loads(raw)
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                chunk = line[len("data:"):].strip()
                if chunk and chunk != "[DONE]":
                    try:
                        return json.loads(chunk)
                    except json.JSONDecodeError:
                        continue
        raise McdMcpError("无法解析 MCP 响应")

    def _post(self, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint, data=data, method="POST", headers=self._headers()
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                sid = resp.headers.get("Mcp-Session-Id")
                if sid:
                    self.session_id = sid
                raw = resp.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise McdMcpError("触发限流(429)，请稍后重试（600 次/分钟上限）") from e
            body = e.read().decode("utf-8", "ignore")
            raise McdMcpError(f"HTTP {e.code}: {body[:500]}") from e
        except urllib.error.URLError as e:
            raise McdMcpError(f"网络错误：{e.reason}") from e
        return self._parse_body(raw)

    # ---- 协议层 ----
    def initialize(self) -> dict:
        resp = self._post({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "mcd-benefits-butler", "version": "0.1.0"},
            },
        })
        if "result" in resp:
            self._server_info = resp["result"].get("serverInfo")
            return resp["result"]
        raise McdMcpError(f"initialize 失败：{resp.get('error')}")

    def call_tool(self, name: str, arguments: dict = None, retries: int = 3):
        last = None
        for attempt in range(retries):
            try:
                resp = self._post({
                    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": name, "arguments": arguments or {}},
                })
                if "result" in resp:
                    return self._extract_text(resp["result"])
                err = resp.get("error", {})
                if "429" in str(err):
                    raise McdMcpError("429")
                raise McdMcpError(f"tools/call({name}) 失败：{err}")
            except McdMcpError as e:
                last = e
                if "429" in str(e):
                    time.sleep(2 ** attempt)
                    continue
                raise
        raise last

    @staticmethod
    def _extract_text(result: dict):
        """result.content 形如 [{type:'text', text:'...'}]。

        mcd-mcp 工具统一返回「Markdown 包裹的完整 JSON」：说明在前，
        真实数据在 '## Original Response' 标题后的一个完整 JSON 对象里。
        优先返回结构化 dict；若无 JSON，则回退为原始 Markdown 文本（供透传展示）。
        """
        texts = []
        for item in result.get("content", []):
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
        joined = "\n".join(texts)
        structured = McdMcpClient._extract_structured(joined)
        return structured if structured is not None else joined

    @staticmethod
    def _extract_structured(text):
        """从工具返回中抽取结构化 JSON。返回 dict，或在无 JSON 时返回 None。"""
        if not isinstance(text, str):
            return None
        s = text.strip()
        # 情况1：整段就是 JSON
        if s.startswith("{"):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                pass
        # 情况2：从 '## Original Response' 之后抽取完整 JSON 对象
        m = re.search(r"##\s*Original\s+Response\s*\n+(.*)", text, re.DOTALL | re.IGNORECASE)
        if m:
            body = m.group(1).strip()
            i = body.find("{")
            j = body.rfind("}")
            if i != -1 and j != -1 and j > i:
                try:
                    return json.loads(body[i:j + 1])
                except json.JSONDecodeError:
                    pass
        return None

    @property
    def server_info(self):
        return self._server_info
