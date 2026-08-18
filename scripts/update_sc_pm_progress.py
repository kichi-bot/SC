"""Generate public aggregate progress data from an SC PM grader export.

The export contains grading totals only. It deliberately excludes answer text,
field-level grading details, and any user account information.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "sc_pm_progress_data.js"


def parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("採点日時が不正です。")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_progress(source: Path) -> dict[str, object]:
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    if payload.get("schemaVersion") != 1 or not isinstance(payload.get("questions"), list):
        raise ValueError("SC午後採点サイトの公開用集計JSONとして読み取れませんでした。")

    questions: list[dict[str, object]] = []
    for item in payload["questions"]:
        if not isinstance(item, dict):
            raise ValueError("問題集計の形式が不正です。")
        exam, question = item.get("exam"), item.get("question")
        score, maximum = item.get("score"), item.get("max")
        graded_at = parse_timestamp(item.get("gradedAt"))
        if not isinstance(exam, str) or not isinstance(question, str) or not exam or not question:
            raise ValueError("試験名または問題名が不正です。")
        if not isinstance(score, (int, float)) or not isinstance(maximum, (int, float)) or maximum <= 0 or not 0 <= score <= maximum:
            raise ValueError("得点が不正です。")
        questions.append({"exam": exam, "question": question, "score": score, "max": maximum, "gradedAt": graded_at})

    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_exam: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in questions:
        by_day[item["gradedAt"].astimezone().date().isoformat()].append(item)
        by_exam[str(item["exam"])].append(item)

    def summarize(label: str, items: list[dict[str, object]]) -> dict[str, object]:
        score = sum(float(item["score"]) for item in items)
        maximum = sum(float(item["max"]) for item in items)
        return {"label": label, "questions": len(items), "score": score, "max": maximum, "accuracy": round(score / maximum * 100, 1) if maximum else 0.0}

    days = [summarize(label, items) for label, items in by_day.items()]
    days.sort(key=lambda item: str(item["label"]), reverse=True)
    exams = [summarize(label, items) for label, items in by_exam.items()]
    exams.sort(key=lambda item: (-int(item["questions"]), str(item["label"])))
    question_maps = []
    for label, items in by_exam.items():
        completed = sorted({str(item["question"]) for item in items}, key=lambda value: int(value.removeprefix("問")))
        question_maps.append({"label": label, "total": 4, "completed": completed})
    question_maps.sort(key=lambda item: str(item["label"]), reverse=True)
    score = sum(float(item["score"]) for item in questions)
    maximum = sum(float(item["max"]) for item in questions)
    exported_at = parse_timestamp(payload.get("exportedAt")).astimezone()
    return {"exportedAt": exported_at.isoformat(timespec="minutes"), "lastStudyDate": days[0]["label"] if days else None, "questions": len(questions), "score": score, "max": maximum, "accuracy": round(score / maximum * 100, 1) if maximum else 0.0, "days": days, "exams": exams, "questionMaps": question_maps}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path, help="SC午後採点サイトから保存した公開用集計JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.report.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    progress = build_progress(source)
    data = json.dumps(progress, ensure_ascii=False, separators=(",", ":"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "// 自動生成: scripts/update_sc_pm_progress.py\n"
        "// SC午後採点サイトの公開用集計値（答案本文・設問別結果は含まない）\n"
        f"window.SC_PM_PROGRESS={data};\n",
        encoding="utf-8",
    )
    print(f"Updated {args.output}: {progress['questions']} questions, {progress['accuracy']}%")


if __name__ == "__main__":
    main()
