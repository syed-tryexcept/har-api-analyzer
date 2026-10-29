import csv
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

BASE_DIR = Path.home() / "Desktop" / "RailwayApiMonitor"
HAR_FILE = BASE_DIR / "har" / "activity.har"
REPORT_DIR = BASE_DIR / "reports"
REPORT_FILE = REPORT_DIR / "api_activity.csv"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = ["seat-layout", "reserve-seat", "release-seat", "passenger-details"]
FIELDS = ["timestamp", "method", "endpoint", "status", "duration_ms", "resource_type"]


def safe_endpoint(url):
    """Keep host and path only; drop query string."""
    try:
        p = urlsplit(url)
        return p.netloc + p.path
    except Exception:
        return "[invalid URL]"


def short(text, width=48):
    """Show only the last part of long endpoints."""
    return text if len(text) <= width else "..." + text[-(width - 3):]


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def main():
    if not HAR_FILE.exists():
        print("HAR file not found!")
        print(f"Expected location: {HAR_FILE}")
        return

    with open(HAR_FILE, encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("log", {}).get("entries", [])
    rows = []
    for e in entries:
        req = e.get("request", {})
        res = e.get("response", {})
        rows.append({
            "timestamp": e.get("startedDateTime", ""),
            "method": req.get("method", ""),
            "endpoint": safe_endpoint(req.get("url", "")),
            "status": to_int(res.get("status", 0)),
            "duration_ms": round(e.get("time", 0), 1),
            "resource_type": e.get("_resourceType", ""),
        })

    with open(REPORT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print("=" * 60)
    print("                    API ACTIVITY REPORT")
    print("=" * 60)
    print(f"Total requests: {len(rows)}")
    print(f"Report saved to: {REPORT_FILE}")

    # ---------- 1. Summary by endpoint ----------
    stats = defaultdict(lambda: {"count": 0, "ok": 0, "fail": 0, "total": 0.0, "max": 0.0})
    for r in rows:
        key = (r["method"], r["endpoint"])
        s = stats[key]
        s["count"] += 1
        s["total"] += r["duration_ms"]
        s["max"] = max(s["max"], r["duration_ms"])
        if 200 <= r["status"] < 400:
            s["ok"] += 1
        else:
            s["fail"] += 1

    print("\n--- 1. Summary by endpoint ---")
    print(f'{"METHOD":<7} {"ENDPOINT":<48} {"COUNT":>5} {"OK":>4} {"FAIL":>5} {"AVG ms":>8} {"MAX ms":>8}')
    for (method, endpoint), s in sorted(stats.items(), key=lambda x: -x[1]["count"]):
        avg = s["total"] / s["count"]
        print(f'{method:<7} {short(endpoint):<48} {s["count"]:>5} {s["ok"]:>4} {s["fail"]:>5} {avg:>8.1f} {s["max"]:>8.1f}')

    # ---------- 2. Errors (4xx / 5xx / failed) ----------
    errors = [r for r in rows if r["status"] >= 400 or r["status"] == 0]
    print(f"\n--- 2. Errors (status 4xx/5xx or failed): {len(errors)} ---")
    if errors:
        for r in errors:
            print(f'{r["timestamp"]} | {r["method"]} | {r["status"]} | '
                  f'{r["duration_ms"]} ms | {short(r["endpoint"], 55)}')
    else:
        print("No errors found.")

    # ---------- 3. Slowest 5 requests ----------
    print("\n--- 3. Slowest 5 requests ---")
    for r in sorted(rows, key=lambda x: -x["duration_ms"])[:5]:
        print(f'{r["duration_ms"]:>8} ms | {r["method"]} | {r["status"]} | {short(r["endpoint"], 55)}')

    # ---------- Selected endpoints ----------
    print("\n--- Selected endpoint activity ---")
    found = False
    for r in rows:
        if any(k in r["endpoint"] for k in KEYWORDS):
            found = True
            print(f'{r["timestamp"]} | {r["method"]} | {r["status"]} | '
                  f'{r["duration_ms"]} ms | {short(r["endpoint"], 55)}')
    if not found:
        print("No selected endpoints found in this log.")

    print("\nDone. This program only analyzes the exported log.")


main()