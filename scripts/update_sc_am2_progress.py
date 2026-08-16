"""Generate public aggregate progress data from a Kakomon Dojo CSV report.

The downloaded report is kept outside the repository. Only aggregate counts are
written to the public site, so individual attempt rows are not published.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "sc_am2_progress_data.js"
REQUIRED_COLUMNS = {"No.", "正誤", "分野名", "大分類", "中分類", "出典", "学習日"}
URL_PATTERN = re.compile(r'https://www\.sc-siken\.com/kakomon/[^"\s,]+')


def read_report(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 or CP932 report and validate its expected columns."""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp932"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        rows = list(csv.DictReader(text.splitlines()))
        if rows and REQUIRED_COLUMNS.issubset(rows[0]):
            return rows
    raise ValueError("過去問道場の学習履歴CSVとして読み取れませんでした。")


def normalize_date(value: str) -> str:
    return datetime.strptime(value.strip(), "%Y/%m/%d").date().isoformat()


def percentage(correct: int, answered: int) -> float:
    return round(correct / answered * 100, 1) if answered else 0.0


def build_progress(rows: list[dict[str, str]], source_path: Path) -> dict[str, object]:
    status_counts = Counter(row["正誤"].strip() for row in rows)
    correct = status_counts["○"]
    wrong = status_counts["×"]
    unanswered = status_counts["-"]
    answered = correct + wrong

    daily: dict[str, Counter[str]] = {}
    categories: dict[str, Counter[str]] = {}
    source_urls: set[str] = set()

    for row in rows:
        status = row["正誤"].strip()
        date = normalize_date(row["学習日"])
        category = row["中分類"].strip() or "その他"
        daily.setdefault(date, Counter())[status] += 1
        categories.setdefault(category, Counter())[status] += 1
        match = URL_PATTERN.search(row["出典"])
        if match:
            source_urls.add(match.group(0))

    def summarize(label: str, counts: Counter[str]) -> dict[str, object]:
        item_correct = counts["○"]
        item_wrong = counts["×"]
        item_answered = item_correct + item_wrong
        return {
            "label": label,
            "total": sum(counts.values()),
            "correct": item_correct,
            "wrong": item_wrong,
            "accuracy": percentage(item_correct, item_answered),
        }

    daily_summary = [summarize(date, daily[date]) for date in sorted(daily, reverse=True)]
    category_summary = [summarize(name, counts) for name, counts in categories.items()]
    category_summary.sort(key=lambda item: (-int(item["total"]), str(item["label"])))

    downloaded_at = datetime.fromtimestamp(source_path.stat().st_mtime).astimezone()
    return {
        "downloadedAt": downloaded_at.isoformat(timespec="minutes"),
        "lastStudyDate": daily_summary[0]["label"] if daily_summary else None,
        "total": len(rows),
        "answered": answered,
        "correct": correct,
        "wrong": wrong,
        "unanswered": unanswered,
        "accuracy": percentage(correct, answered),
        "uniqueQuestions": len(source_urls),
        "days": daily_summary,
        "categories": category_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path, help="過去問道場からダウンロードした学習履歴CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source_path = args.report.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    progress = build_progress(read_report(source_path), source_path)
    payload = json.dumps(progress, ensure_ascii=False, separators=(",", ":"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "// 自動生成: scripts/update_sc_am2_progress.py\n"
        "// 過去問道場の学習履歴CSVから作成した公開用の集計値（個別履歴は含まない）\n"
        f"window.SC_AM2_PROGRESS={payload};\n",
        encoding="utf-8",
    )
    print(
        f"Updated {args.output}: {progress['total']} attempts, "
        f"{progress['correct']} correct, {progress['accuracy']}%"
    )


if __name__ == "__main__":
    main()
