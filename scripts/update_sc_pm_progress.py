"""Generate public aggregate progress data from an SC PM grader export.

The export contains grading totals only. It deliberately excludes answer text,
field-level grading details, and any user account information. Attempt totals
remain separate while the legacy top-level summary reflects each question's
latest attempt.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "sc_pm_progress_data.js"
PROGRESS_PATTERN = re.compile(r"window\.SC_PM_PROGRESS=(\{.*\});\s*$", re.S)
PM_EXAM_IDS = [
    "07_aki", "07_haru", "06_aki", "06_haru", "05_aki", "05_haru", "04_aki", "04_haru",
    "03_aki", "03_haru", "02_aki", "01_aki", "31_haru", "30_aki", "30_haru", "29_aki",
    "29_haru", "28_aki", "28_haru", "27_aki", "27_haru", "26_aki", "26_haru", "25_aki",
    "25_haru", "24_aki", "24_haru", "23_aki", "23_toku", "22_aki", "22_haru", "21_aki", "21_haru",
]
UNIFIED_PM_EXAMS = {"07_aki", "07_haru", "06_aki", "06_haru", "05_aki"}
NUMBER_PATTERN = re.compile(r"\d+")


def parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("採点日時が不正です。")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def exam_label(exam_id: str) -> str:
    year, season = exam_id.split("_", 1)
    suffix = "春期" if season == "haru" else "秋期" if season == "aki" else "特別"
    if int(year) <= 7:
        era_year = "元" if int(year) == 1 else str(int(year))
        return f"令和{era_year}年{suffix}"
    return f"平成{int(year)}年{suffix}"


def exam_items(exam_id: str) -> list[dict[str, str]]:
    if exam_id in UNIFIED_PM_EXAMS:
        return [{"key": f"問{number}", "label": f"問{number}"} for number in range(1, 5)]
    return [
        {"key": "問1", "label": "午後Ⅰ 問1"}, {"key": "問2", "label": "午後Ⅰ 問2"},
        {"key": "問3", "label": "午後Ⅰ 問3"}, {"key": "問4", "label": "午後Ⅱ 問1"},
        {"key": "問5", "label": "午後Ⅱ 問2"},
    ]


def map_question_key(exam_id: str, question: str) -> str:
    """Convert grader labels to the stable key used by the public study map."""
    items = exam_items(exam_id)
    for item in items:
        if question == item["key"] or question == item["label"]:
            return item["key"]
    return question


def build_progress(sources: list[Path]) -> dict[str, object]:
    latest_question_attempts: dict[tuple[str, str, int], dict[str, object]] = {}
    exported_times: list[datetime] = []
    for source in sources:
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
        schema_version = payload.get("schemaVersion")
        if schema_version not in (1, 2) or not isinstance(payload.get("questions"), list):
            raise ValueError(f"SC午後採点サイトの公開用集計JSONとして読み取れませんでした: {source}")
        exported_times.append(parse_timestamp(payload.get("exportedAt")))

        for item in payload["questions"]:
            if not isinstance(item, dict):
                raise ValueError("問題集計の形式が不正です。")
            exam, question = item.get("exam"), item.get("question")
            score, maximum = item.get("score"), item.get("max")
            attempt = item.get("attempt", 1)
            graded_at = parse_timestamp(item.get("gradedAt"))
            if not isinstance(exam, str) or not isinstance(question, str) or not exam or not question:
                raise ValueError("試験名または問題名が不正です。")
            if not isinstance(score, (int, float)) or not isinstance(maximum, (int, float)) or maximum <= 0 or not 0 <= score <= maximum:
                raise ValueError("得点が不正です。")
            if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
                raise ValueError("演習回が不正です。")
            normalized = {"exam": exam, "question": question, "attempt": attempt, "score": score, "max": maximum, "gradedAt": graded_at}
            key = (exam, question, attempt)
            if key not in latest_question_attempts or graded_at > latest_question_attempts[key]["gradedAt"]:
                latest_question_attempts[key] = normalized

    question_attempts = list(latest_question_attempts.values())
    latest_questions: dict[tuple[str, str], dict[str, object]] = {}
    for item in question_attempts:
        key = (str(item["exam"]), str(item["question"]))
        current = latest_questions.get(key)
        if current is None or (int(item["attempt"]), item["gradedAt"]) > (int(current["attempt"]), current["gradedAt"]):
            latest_questions[key] = item
    questions = list(latest_questions.values())

    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_exam: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in questions:
        by_day[item["gradedAt"].astimezone().date().isoformat()].append(item)
        by_exam[str(item["exam"])].append(item)

    by_attempt: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for item in question_attempts:
        by_attempt[(str(item["exam"]), int(item["attempt"]))].append(item)

    def summarize(label: str, items: list[dict[str, object]]) -> dict[str, object]:
        score = sum(float(item["score"]) for item in items)
        maximum = sum(float(item["max"]) for item in items)
        return {"label": label, "questions": len(items), "score": score, "max": maximum, "accuracy": round(score / maximum * 100, 1) if maximum else 0.0}

    days = [summarize(label, items) for label, items in by_day.items()]
    days.sort(key=lambda item: str(item["label"]), reverse=True)
    exams = [summarize(label, items) for label, items in by_exam.items()]
    exams.sort(key=lambda item: (-int(item["questions"]), str(item["label"])))
    attempts = []
    for (exam, attempt), items in by_attempt.items():
        summary = summarize(f"{exam} {attempt}回目", items)
        summary.update({"exam": exam, "attempt": attempt})
        attempts.append(summary)
    attempts.sort(key=lambda item: (str(item["exam"]), int(item["attempt"])))
    question_maps = []
    known_maps = [(exam_id, exam_label(exam_id)) for exam_id in PM_EXAM_IDS]
    known_labels = {label for _, label in known_maps}
    for exam_id, label in known_maps + [("custom", label) for label in sorted(set(by_exam).difference(known_labels), reverse=True)]:
        items = by_exam.get(label, [])
        completed = sorted(
            {map_question_key(exam_id, str(item["question"])) for item in items},
            key=lambda value: int(NUMBER_PATTERN.search(value).group()) if NUMBER_PATTERN.search(value) else 0,
        )
        map_items = exam_items(exam_id) if exam_id != "custom" else [{"key": f"問{number}", "label": f"問{number}"} for number in range(1, 5)]
        question_maps.append({"label": label, "total": len(map_items), "items": map_items, "completed": completed})
    exam_order = {label: index for index, (_, label) in enumerate(known_maps)}

    def question_sort_key(item: dict[str, object]) -> tuple[int, str, int, int]:
        label = str(item["exam"])
        match = NUMBER_PATTERN.search(str(item["question"]))
        return (exam_order.get(label, len(exam_order)), label, int(match.group()) if match else 0, int(item["attempt"]))

    # 問ごとの得点（設問別の採点結果や答案本文は含まない）。演習回ごとに1件。
    question_results = []
    for item in sorted(question_attempts, key=question_sort_key):
        score_value = float(item["score"])
        max_value = float(item["max"])
        question_results.append({
            "exam": item["exam"],
            "question": item["question"],
            "attempt": int(item["attempt"]),
            "score": score_value,
            "max": max_value,
            "accuracy": round(score_value / max_value * 100, 1) if max_value else 0.0,
            "gradedAt": item["gradedAt"].astimezone().isoformat(timespec="minutes"),
        })
    score = sum(float(item["score"]) for item in questions)
    maximum = sum(float(item["max"]) for item in questions)
    exported_at = max(exported_times).astimezone()
    return {
        "exportedAt": exported_at.isoformat(timespec="minutes"),
        "lastStudyDate": days[0]["label"] if days else None,
        "questions": len(questions),
        "score": score,
        "max": maximum,
        "accuracy": round(score / maximum * 100, 1) if maximum else 0.0,
        "attemptRecords": len(question_attempts),
        "attempts": attempts,
        "questionResults": question_results,
        "days": days,
        "exams": exams,
        "questionMaps": question_maps,
    }


def existing_manual_progress(output: Path) -> dict[str, object]:
    if not output.is_file():
        return {}
    match = PROGRESS_PATTERN.search(output.read_text(encoding="utf-8"))
    if not match:
        return {}
    try:
        current = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}
    return {
        key: current[key]
        for key in ("manualSavedAt", "manualChecked", "manualItems", "manualMap")
        if key in current
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", type=Path, nargs="+", help="SC午後採点サイトから保存した公開用集計JSON（複数指定可）")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    sources = [report.resolve() for report in args.reports]
    for source in sources:
        if not source.is_file():
            raise FileNotFoundError(source)
    progress = build_progress(sources)
    progress.update(existing_manual_progress(args.output))
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
