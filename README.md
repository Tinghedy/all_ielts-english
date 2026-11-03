# IELTS English — 聽說讀寫總覽

> 目標：2026-10 中 起兩個月內，四項各往上提升一級。

## 介面（記單字 / 每日紀錄）
同一份 `index.html` 兩種用法，資料都直接寫回本專案的 Markdown 檔，沒有外部資料庫：
- **線上（GitHub Pages）**：打開 Pages 網址 → 「設定」填 GitHub token（存檔用）與 Gemini key。每次存檔 = 一個 commit
- **本機**：雙擊 `start.command`（或 `python3 app/server.py`）→ http://127.0.0.1:5178，Gemini key 放 `.env`
- 本機跟線上會各自改檔，換邊用之前先 `git pull` / `git push`
- 隨手記 → `05-vocabulary/inbox.md`；在 `.env` 填 `GEMINI_API_KEY` 後，每筆會由 Gemini 校正並加中文說明
- 記單字 → `05-vocabulary/` 對應主題檔與段落；新主題會自動建檔並加進字彙 README
- 每日紀錄 → `0X-skill/log/` 新檔 + `progress-log.md` 加一列 + 勾選的技能卡練習紀錄 / 狀態

## 結構
| 資料夾 | 用途 |
|---|---|
| `00-dashboard` | 每日進度總表、每週回顧 |
| `01-listening` ~ `04-writing` | 四項技能，各自有 `skills/`（必要技能卡）與 `log/`（每日紀錄） |
| `05-vocabulary` | 四項共用的主題字彙（高 / 中 / 低頻） |
| `06-templates` | 每日紀錄、技能卡、錯題卡模板 |
| `07-resources` | 題本、影片、網站連結 |
| `index.html`、`app` | 介面頁面（GitHub Pages）與本機伺服器（Python 內建，免安裝） |

## 每個技能資料夾長這樣
```
0X-skill/
├── README.md     ← 技能樹 + 目前狀態
├── skills/       ← 必要 skill，一張卡一個題型 / 能力
├── log/          ← YYYY-MM-DD-描述.md 每日紀錄
└── mistakes/     ← 錯題 & 卡關點
```

## 狀態標記
🔴 未開始　🟡 練習中　🟢 穩定

## 命名規則
- 每日紀錄：`YYYY-MM-DD-簡短描述.md`（例：`2026-10-30-cam18-test1.md`）
- 技能卡：`題型英文名.md`（例：`true-false-not-given.md`）
- 錯題：`YYYY-MM-DD-題型.md`
