#!/usr/bin/env python3
"""IELTS 學習庫的本機伺服器：提供 index.html，並讓頁面讀寫專案裡的 Markdown 檔、轉送 Gemini 請求。

紀錄邏輯都在 index.html；同一份頁面放到 GitHub Pages 時改走 GitHub API。
啟動：python3 app/server.py  → 打開 http://127.0.0.1:5178
"""
import json
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("PORT", 5178))
DEFAULT_MODEL = "gemini-flash-lite-latest"


def load_env():
    """讀專案根目錄的 .env（KEY=VALUE），不覆蓋已存在的環境變數。"""
    env = ROOT / ".env"
    if env.exists():
        for l in env.read_text(encoding="utf-8").splitlines():
            k, sep, v = l.partition("=")
            if sep and not l.lstrip().startswith("#"):
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def resolve(rel, want_md=True):
    """只允許 0X-資料夾 底下的檔案，避免讀寫到 .env 或程式碼。"""
    p = (ROOT / rel).resolve()
    try:
        parts = p.relative_to(ROOT).parts
    except ValueError:
        raise ValueError("路徑不允許")
    if not parts or not re.fullmatch(r"0\d-[\w-]+", parts[0]) or any(x.startswith(".") for x in parts):
        raise ValueError("路徑不允許")
    if want_md and p.suffix != ".md":
        raise ValueError("只能讀寫 .md")
    return p


def gemini(body):
    load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return 400, {"error": {"message": "未設定 GEMINI_API_KEY（.env）"}}
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return 200, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


class Handler(BaseHTTPRequestHandler):
    def send(self, code, data, ctype="application/json; charset=utf-8"):
        body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path in ("/", "/index.html"):
                return self.send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/config":
                load_env()
                return self.send(200, {"mode": "local", "gemini": bool(os.environ.get("GEMINI_API_KEY"))})
            if u.path == "/api/fs":
                p = resolve(q.get("path", ""))
                if not p.exists():
                    return self.send(404, {"error": "not found"})
                return self.send(200, {"content": p.read_text(encoding="utf-8")})
            if u.path == "/api/ls":
                p = resolve(q.get("dir", ""), want_md=False)
                names = sorted(f.name for f in p.glob("*.md")) if p.is_dir() else []
                return self.send(200, names)
            self.send(404, {"error": "not found"})
        except ValueError as e:
            self.send(400, {"error": str(e)})
        except Exception as e:
            self.send(500, {"error": str(e)})

    def do_POST(self):
        # 只接受本機頁面送來的請求
        origin = self.headers.get("Origin", "")
        if origin and not re.fullmatch(rf"http://(127\.0\.0\.1|localhost):{PORT}", origin):
            return self.send(403, {"error": "forbidden"})
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/api/fs":
                p = resolve(data.get("path", ""))
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(data.get("content", ""), encoding="utf-8")
                return self.send(200, {"ok": True})
            if self.path == "/api/gemini":
                return self.send(*gemini(data))
            self.send(404, {"error": "not found"})
        except ValueError as e:
            self.send(400, {"error": str(e)})
        except Exception as e:
            self.send(500, {"error": str(e)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"IELTS 學習庫介面：http://127.0.0.1:{PORT}  （Ctrl+C 結束）")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
