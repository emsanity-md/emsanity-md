#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
USERNAME = "emsanity-md"
URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_days(html_text: str) -> list[dict[str, int | str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    days: list[dict[str, int | str]] = []
    tooltip_counts: dict[str, int] = {}
    for tip in soup.select("tool-tip[for]"):
        text = tip.get_text(" ", strip=True)
        ref = tip.get("for")
        if not ref:
            continue
        if text.lower().startswith("no contributions"):
            tooltip_counts[ref] = 0
            continue
        match = re.search(r"(\d+)\s+contributions?\s+on\s+", text, flags=re.IGNORECASE)
        if match:
            tooltip_counts[ref] = int(match.group(1))

    for cell in soup.select("[data-date][data-level]"):
        d = cell.get("data-date")
        if not d:
            continue
        cell_id = cell.get("id", "")
        count = int(cell.get("data-count", tooltip_counts.get(cell_id, 0)))
        level = int(cell.get("data-level", "0"))
        days.append({"date": d, "count": count, "level": level})
    days.sort(key=lambda x: x["date"])
    return days


def streaks(days: list[dict[str, int | str]]) -> tuple[int, int]:
    current = 0
    longest = 0
    running = 0
    last_active: date | None = None

    for item in days:
        d = datetime.strptime(str(item["date"]), "%Y-%m-%d").date()
        active = int(item["count"]) > 0
        if active:
            if last_active and (d - last_active).days == 1:
                running += 1
            else:
                running = 1
            last_active = d
            longest = max(longest, running)
        else:
            running = 0

    if days:
        for item in reversed(days):
            if int(item["count"]) > 0:
                current += 1
            else:
                break
    return current, longest


def monthly_totals(days: list[dict[str, int | str]]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for d in days:
        month = str(d["date"])[:7]
        totals[month] += int(d["count"])
    return dict(sorted(totals.items()))


def fetch() -> dict[str, object]:
    res = requests.get(URL, timeout=30)
    res.raise_for_status()

    days = parse_days(res.text)
    current, longest = streaks(days)
    best = max(days, key=lambda x: int(x["count"]), default={"date": "", "count": 0})
    total = sum(int(d["count"]) for d in days)

    return {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": URL,
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": int(best["count"])},
        "monthly_totals": monthly_totals(days),
        "days": days,
    }


def main() -> None:
    payload = fetch()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
