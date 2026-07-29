# 📅 財經行事曆 — Financial Calendar

追蹤重大財經事件、財報、總經數據的全端應用。

## 專案結構

```
financial-calendar/
├── static/                # 前端靜態檔案
│   ├── index.html         # 事件檢視器（自動隱藏過去事件）
│   └── data/events.json   # 事件 JSON 資料
├── api/
│   └── server.py          # FastAPI 伺服器
├── scripts/
│   └── md2json.py         # Markdown → JSON 轉換工具
├── events.md              # 可疊加的 Markdown 行事曆（主要編輯入口）
├── requirements.txt       # Python 相依套件
└── README.md
```

## 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 啟動伺服器
```bash
uvicorn api.server:app --reload
```

開啟 http://localhost:8000 即可瀏覽。

### 3. 新增事件
編輯 `events.md`，按格式加入新事件，然後執行：
```bash
python scripts/md2json.py
```
重新整理瀏覽器即可看到更新。

## API 文件

啟動後瀏覽 http://localhost:8000/api/docs

| 端點 | 說明 | 參數 |
|------|------|------|
| `GET /api/events` | 所有事件（可篩選） | `future_only`, `min_importance`, `category`, `date_from`, `date_to` |
| `GET /api/events/today` | 今日事件 | — |
| `GET /api/events/range?days=14` | 未來 N 天事件 | `days` |
| `GET /api/health` | 健康檢查 | — |

## 事件 Markdown 格式

```markdown
### YYYY-MM-DD（星期）
| 時間 | **事件名稱** | ⭐⭐⭐⭐⭐ | 分類 | 標的 | 備註 |
```

直接在 `events.md` 中新增行即可，轉換工具會自動解析。

## 部署

### Render / Railway
連接到 GitHub repo，選擇 `api/server.py` 作為啟動入口：
```bash
uvicorn api.server:app --host 0.0.0.0 --port $PORT
```

### Docker（選用）
```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```
