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
QUESTION_URL_PATTERN = re.compile(r"/kakomon/(?P<exam>[^/]+)/am2_(?P<number>\d+)\.html$")
EXAM_ORDER = [
    "07_aki", "07_haru", "06_aki", "06_haru", "05_aki", "05_haru", "04_aki", "04_haru",
    "03_aki", "03_haru", "02_aki", "01_aki", "31_haru", "30_aki", "30_haru", "29_aki",
    "29_haru", "28_aki", "28_haru", "27_aki", "27_haru", "26_aki", "26_haru", "25_aki",
    "25_haru", "24_aki", "24_haru", "23_aki", "23_toku", "22_aki", "22_haru", "21_aki", "21_haru",
]


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


def exam_label(exam_id: str) -> str:
    year, season = exam_id.split("_", 1)
    suffix = "春期" if season == "haru" else "秋期" if season == "aki" else "特別"
    if year.isdigit() and int(year) <= 7:
        era_year = "元" if int(year) == 1 else str(int(year))
        return f"令和{era_year}年{suffix}"
    return f"平成{int(year)}年{suffix}"


def build_progress(rows: list[dict[str, str]], source_path: Path) -> dict[str, object]:
    status_counts = Counter(row["正誤"].strip() for row in rows)
    correct = status_counts["○"]
    wrong = status_counts["×"]
    unanswered = status_counts["-"]
    answered = correct + wrong

    daily: dict[str, Counter[str]] = {}
    categories: dict[str, Counter[str]] = {}
    source_urls: set[str] = set()
    exam_questions: dict[str, set[int]] = {}

    for row in rows:
        status = row["正誤"].strip()
        date = normalize_date(row["学習日"])
        category = row["中分類"].strip() or "その他"
        daily.setdefault(date, Counter())[status] += 1
        categories.setdefault(category, Counter())[status] += 1
        match = URL_PATTERN.search(row["出典"])
        if match:
            source_url = match.group(0)
            source_urls.add(source_url)
            question_match = QUESTION_URL_PATTERN.search(source_url)
            if question_match:
                exam_questions.setdefault(question_match.group("exam"), set()).add(int(question_match.group("number")))

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
    exam_maps = [
        {"id": exam_id, "label": exam_label(exam_id), "total": 25, "completed": sorted(exam_questions.get(exam_id, set()))}
        for exam_id in EXAM_ORDER
    ]

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
        "examMaps": exam_maps,
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
