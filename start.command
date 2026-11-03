#!/bin/bash
# 雙擊啟動 IELTS 學習庫介面
cd "$(dirname "$0")"
(sleep 1 && open http://127.0.0.1:5178) &
python3 app/server.py
