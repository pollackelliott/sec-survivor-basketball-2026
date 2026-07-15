"""One-time importer for SEC 2025-26 conference scores.

Usage after installing pandas/lxml/requests:
    python scripts/import_results.py

This writes data/results.json. The static website reads that JSON and never scrapes live.
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.sports-reference.com/cbb/conferences/sec/men/2026-schedule.html"

ALIASES = {
    "Mississippi": "Ole Miss",
    "Louisiana State": "LSU",
}

def clean_team(name):
    name = str(name).replace("NCAA", "").strip()
    name = ALIASES.get(name, name)
    return name

def main():
    tables = pd.read_html(URL)
    df = max(tables, key=len)
    # Sports-Reference column names can shift slightly; inspect if this fails.
    cols = {str(c).lower(): c for c in df.columns}
    date_col = next(c for c in df.columns if str(c).lower() in {"date", "date/time"} or "date" in str(c).lower())
    visitor_col = next(c for c in df.columns if "visitor" in str(c).lower() or "away" in str(c).lower())
    home_col = next(c for c in df.columns if "home" in str(c).lower())
    visitor_pts_col = next(c for c in df.columns if "visitor" in str(c).lower() and ("pts" in str(c).lower() or "points" in str(c).lower()))
    home_pts_col = next(c for c in df.columns if "home" in str(c).lower() and ("pts" in str(c).lower() or "points" in str(c).lower()))

    results = []
    for _, row in df.iterrows():
        if pd.isna(row.get(visitor_pts_col)) or pd.isna(row.get(home_pts_col)):
            continue
        date = pd.to_datetime(row[date_col]).date().isoformat()
        results.append({
            "date": date,
            "away": clean_team(row[visitor_col]),
            "home": clean_team(row[home_col]),
            "awayScore": int(row[visitor_pts_col]),
            "homeScore": int(row[home_pts_col]),
            "source": "sports-reference"
        })
    out = ROOT / "data" / "results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} results to {out}")

if __name__ == "__main__":
    main()
