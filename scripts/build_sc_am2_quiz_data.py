"""Build the browser-ready SC morning II quiz dataset.

The study page is intentionally self-contained so that it also works when its
HTML file is opened directly from disk.  This script merges the full question
text from sc_kakomon.json with the category metadata used by the dashboard.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sc_kakomon.json"
METADATA = ROOT / "data" / "sc_am2_questions.csv"
OUTPUT = ROOT / "docs" / "assets" / "sc_am2_quiz_data.js"


def parse_period(period: str) -> tuple[int, str]:
    """Return the Gregorian year and CSV season for an exam period."""
    if period == "平成23年特別":
        # 東日本大震災による日程変更で、平成23年春期の代替として実施された回。
        return 2011, "spring"

    match = re.fullmatch(r"令和(元|\d+)年(春期|秋期)", period)
    if match:
        era_year = 1 if match.group(1) == "元" else int(match.group(1))
        return 2018 + era_year, "spring" if match.group(2) == "春期" else "autumn"

    match = re.fullmatch(r"平成(\d+)年(春期|秋期)", period)
    if match:
        return 1988 + int(match.group(1)), "spring" if match.group(2) == "春期" else "autumn"

    raise ValueError(f"Unsupported examination period: {period}")


def source_url(period: str, number: int) -> str:
    """Build the source-page URL, useful when the original diagram is needed."""
    if period == "平成23年特別":
        return f"https://www.sc-siken.com/kakomon/23_toku/am2_{number}.html"

    match = re.fullmatch(r"(令和|平成)(元|\d+)年(春期|秋期)", period)
    if not match:
        return ""
    era_year = 1 if match.group(2) == "元" else int(match.group(2))
    suffix = "haru" if match.group(3) == "春期" else "aki"
    return f"https://www.sc-siken.com/kakomon/{era_year:02d}_{suffix}/am2_{number}.html"


def main() -> None:
    with METADATA.open(encoding="utf-8-sig", newline="") as file:
        metadata = list(csv.DictReader(file))

    metadata_by_key = {
        (int(row["exam_year"]), row["season"], int(row["question_no"])): row
        for row in metadata
    }

    questions = json.loads(SOURCE.read_text(encoding="utf-8"))
    output = []
    for item in questions:
        if item["section"] != "午前Ⅱ":
            continue

        try:
            year, season = parse_period(item["period"])
        except ValueError:
            # 平成23年特別のように、ダッシュボード集計の対象外の回は除く。
            continue
        key = (year, season, item["number"])
        info = metadata_by_key.get(key)
        if not info:
            continue

        choices = [[label, text] for label, text in item["choices"].items()]
        complete = len(choices) >= 2 and item["answer"] in item["choices"]

        output.append(
            {
                "id": f"{year}-{season}-{item['number']}",
                "period": item["period"],
                "year": year,
                "season": season,
                "number": item["number"],
                "question": item["question"],
                "choices": choices,
                "answer": item["answer"],
                "explanation": item["explanation"],
                "available": complete,
                "category": info["main_category"],
                "subcategory": info["sub_category"],
                "priority": info["priority"],
                "sourceUrl": source_url(item["period"], item["number"]),
            }
        )

    if len(output) != len(metadata):
        raise ValueError(f"Expected {len(metadata)} morning II questions, generated {len(output)}")

    output.sort(key=lambda item: (item["year"], item["season"] == "autumn", item["number"]), reverse=True)
    data = json.dumps(output, ensure_ascii=False, separators=(",", ":"))
    OUTPUT.write_text(
        "// 自動生成: scripts/build_sc_am2_quiz_data.py\n"
        "// 問題文・選択肢・正解・解説を含む、午前Ⅱ 825問の演習用データ\n"
        f"window.SC_AM2_QUIZ_QUESTIONS={data};\n",
        encoding="utf-8",
    )
    available = sum(item["available"] for item in output)
    print(f"Generated {len(output)} questions ({available} ready for practice): {OUTPUT}")


if __name__ == "__main__":
    main()
