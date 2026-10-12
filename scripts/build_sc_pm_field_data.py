"""Generate docs/assets/sc_pm_field_data.js: 午後問題ごとの出題分野と題名。

docs/sc_am2_index.html の「解いた過去問マップ」（午後）で、各問の主分野・題名・
キーワードを表示するための静的データを作る。

入力:
  data/sc_field_matrix_fields.json   fields（分野定義）, pmQuestions（R3春〜 の分類）,
                                     pmQuestionsLegacy（H21春〜R2秋 の題名ベース推定）
  html/sc_pm_grader.js               令和7年秋期の問題題名
  html/sc_pm_past_exam_data.js       令和5年秋期〜令和7年春期の問題題名
  html/sc_pm_legacy_exam_data.js     平成21年春期〜令和5年春期の問題題名

試験の並びと問キー（問1, 問2, ...）は scripts/update_sc_pm_progress.py と共有する。
分類や題名を直したら `py -3 scripts/build_sc_pm_field_data.py` を再実行する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from update_sc_pm_progress import PM_EXAM_IDS, exam_items, exam_label  # noqa: E402

FIELDS_PATH = ROOT / "data" / "sc_field_matrix_fields.json"
GRADER_JS = ROOT / "html" / "sc_pm_grader.js"
PAST_JS = ROOT / "html" / "sc_pm_past_exam_data.js"
LEGACY_JS = ROOT / "html" / "sc_pm_legacy_exam_data.js"
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "sc_pm_field_data.js"

EXAM_RE = re.compile(r"id:\s*'([a-z0-9]+)',\s*label:\s*'[^']*',\s*period:\s*'([^']*)'")
QUESTION_RE = re.compile(r"id:\s*'q\d',\s*number:\s*'([^']*)',\s*theme:\s*'([^']*)',\s*title:\s*'([^']*)'")


def titles_from_js(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    """Read question titles from the hand-written grader data (single-quoted JS objects)."""
    text = path.read_text(encoding="utf-8")
    text = text.split("var EXAMS", 1)[0]
    exams = list(EXAM_RE.finditer(text))
    found: dict[tuple[str, str], dict[str, str]] = {}
    for index, match in enumerate(exams):
        end = exams[index + 1].start() if index + 1 < len(exams) else len(text)
        period = match.group(2)
        for question in QUESTION_RE.finditer(text, match.end(), end):
            number, theme, title = question.groups()
            found[(period, number)] = {"title": title, "hint": theme}
    return found


def titles_from_legacy(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text[text.index("=") + 1:].strip().rstrip(";"))
    found: dict[tuple[str, str], dict[str, str]] = {}
    for exam in data:
        for question in exam["questions"]:
            found[(exam["period"], question["number"])] = {"title": question["title"], "hint": ""}
    return found


def split_theme(theme: str) -> tuple[str, str]:
    """'Web/開発/IR：格納型XSS・CSP回避' -> ('Web/開発/IR', '格納型XSS・CSP回避')."""
    if "：" in theme:
        head, tail = theme.split("：", 1)
        return head.strip(), tail.strip()
    return "", theme.strip()


def build() -> tuple[dict, list[str]]:
    cfg = json.loads(FIELDS_PATH.read_text(encoding="utf-8"))
    fields = [
        {"key": f["key"], "id": f["id"], "name": f["name"], "short": f.get("short") or f["name"], "group": f.get("group", "")}
        for f in cfg["fields"]
    ]
    valid = {f["key"] for f in fields}

    classification: dict[tuple[str, str], dict] = {}
    for estimated, entries in ((False, cfg.get("pmQuestions", [])), (True, cfg.get("pmQuestionsLegacy", []))):
        for entry in entries:
            key = (entry["exam"], entry["question"])
            if key in classification:
                raise ValueError(f"分類が重複しています: {key}")
            if entry["primary"] not in valid or any(s not in valid for s in entry.get("secondary", [])):
                raise ValueError(f"未知の分野キー: {key} {entry}")
            classification[key] = dict(entry, estimated=estimated)

    titles: dict[tuple[str, str], dict[str, str]] = {}
    titles.update(titles_from_legacy(LEGACY_JS))
    titles.update(titles_from_js(PAST_JS))
    titles.update(titles_from_js(GRADER_JS))

    warnings: list[str] = []
    exams = []
    used: set[tuple[str, str]] = set()
    for exam_id in PM_EXAM_IDS:
        label = exam_label(exam_id)
        questions = []
        for item in exam_items(exam_id):
            lookup = (label, item["label"])
            used.add(lookup)
            entry = classification.get(lookup)
            title = titles.get(lookup)
            if entry is None:
                warnings.append(f"分類なし: {label} {item['label']}")
            if title is None:
                warnings.append(f"題名なし: {label} {item['label']}")
            head, keywords = split_theme(entry["theme"]) if entry else ("", "")
            questions.append({
                "key": item["key"],
                "label": item["label"],
                "title": title["title"] if title else "",
                "primary": entry["primary"] if entry else "",
                "secondary": list(entry.get("secondary", [])) if entry else [],
                "theme": entry["theme"] if entry else "",
                "themeFields": head,
                "keywords": keywords,
                "estimated": bool(entry["estimated"]) if entry else False,
            })
        exams.append({"label": label, "questions": questions})

    for key in sorted(set(classification) - used):
        warnings.append(f"マップに無い分類: {key[0]} {key[1]}")
    for key in sorted(set(titles) - used):
        warnings.append(f"マップに無い題名: {key[0]} {key[1]}")

    return {
        "generatedAt": datetime.now().astimezone().isoformat(timespec="minutes"),
        "fields": fields,
        "exams": exams,
    }, warnings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data, warnings = build()
    for line in warnings:
        print("warning:", line)
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "// 自動生成: scripts/build_sc_pm_field_data.py\n"
        "// 午後問題ごとの出題分野（主分野・副分野）と題名。分類の正本は data/sc_field_matrix_fields.json\n"
        f"window.SC_PM_FIELDS={text};\n",
        encoding="utf-8",
    )
    total = sum(len(exam["questions"]) for exam in data["exams"])
    classified = sum(1 for exam in data["exams"] for q in exam["questions"] if q["primary"])
    print(f"Wrote {args.output}: {len(data['exams'])} exams, {total} questions, {classified} classified")


if __name__ == "__main__":
    main()
