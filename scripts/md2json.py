"""
將 events.md 轉換為 data/events.json

用法：python scripts/md2json.py
"""

import re, json, os, sys
from datetime import date

MD_PATH = os.path.join(os.path.dirname(__file__), "..", "events.md")
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")

def parse_table_row(line):
    parts = [p.strip() for p in line.split("|")]
    parts = [p for p in parts if p]
    if len(parts) < 6:
        return None

    time = parts[0]
    name = re.sub(r'\*\*(.*?)\*\*', r'\1', parts[1]).strip()
    imp_raw = parts[2].strip()
    importance = sum(1 for c in imp_raw if c == '⭐') or 5
    category = parts[3].strip()
    tickers_raw = parts[4].strip()
    tickers = re.findall(r'[A-Z]{2,5}', tickers_raw) if tickers_raw else []
    note = parts[5].strip() if len(parts) > 5 else ""

    return {
        "time": time,
        "name": name,
        "importance": min(importance, 5),
        "category": category,
        "tickers": tickers,
        "note": note
    }

def parse_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    date_pattern = re.compile(r'###\s+(\d{4}-\d{2}-\d{2})')
    sep_pattern = re.compile(r'^\|[\s\-]+\|')
    row_pattern = re.compile(r'^\|')

    result = []
    current_date = None
    in_table = False

    for line in lines:
        line = line.rstrip()

        d_m = date_pattern.match(line)
        if d_m:
            current_date = d_m.group(1)
            in_table = False
            continue

        if current_date and row_pattern.match(line):
            if sep_pattern.match(line):
                in_table = True
                continue
            if in_table:
                row = parse_table_row(line)
                if row:
                    result.append({"date": current_date, **row})

    return result

def group_by_date(events):
    groups = {}
    day_map = {
        0: "日", 1: "一", 2: "二", 3: "三",
        4: "四", 5: "五", 6: "六"
    }
    for ev in events:
        d = ev["date"]
        if d not in groups:
            dt = date.fromisoformat(d)
            groups[d] = {
                "date": d,
                "day": day_map[dt.weekday()],
                "events": []
            }
        groups[d]["events"].append({
            "time": ev["time"],
            "name": ev["name"],
            "importance": ev["importance"],
            "category": ev["category"],
            "tickers": ev["tickers"],
            "note": ev["note"]
        })
    return sorted(groups.values(), key=lambda x: x["date"])

def main():
    if not os.path.exists(MD_PATH):
        print(f"❌ 找不到 {MD_PATH}")
        sys.exit(1)

    events = parse_md(MD_PATH)
    grouped = group_by_date(events)

    output = {
        "updated": date.today().isoformat() + "T00:00:00Z",
        "events": grouped
    }

    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(d["events"]) for d in grouped)
    print(f"[OK] 已轉換 {total} 個事件 -> {JSON_PATH}")

if __name__ == "__main__":
    main()
