# -*- coding: utf-8 -*-
"""週次レビューの結果をダッシュボード用の公開データ docs/assets/sc_weekly_review_data.js にまとめる。

入力:
  - outputs/weekly/latest.json（scripts/weekly_sc_review.py の集計値）
  - 11_週次レビュー.md（最新セクションの「判断と変更」「カレンダー変更ログ」「今週の重点」「要対応」）
  - outputs/weekly/snapshots.json（週ごとの推移）
出力:
  - docs/assets/sc_weekly_review_data.js（window.SC_WEEKLY_REVIEW）
公開するのは集計値と計画・判断の文章だけ。答案本文や設問別の採点結果は含めない。

使い方:  py -3 scripts/publish_sc_weekly_review.py
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "outputs" / "weekly" / "latest.json"
SNAPSHOTS = ROOT / "outputs" / "weekly" / "snapshots.json"
REVIEW_MD = ROOT / "11_週次レビュー.md"
OUTPUT = ROOT / "docs" / "assets" / "sc_weekly_review_data.js"
JST = dt.timezone(dt.timedelta(hours=9))
NOTE_HEADINGS = {"judgment": "判断と変更", "calendarLog": "カレンダー変更ログ", "focus": "今週の重点", "todo": "要対応"}


def latest_section(text: str) -> str:
    parts = re.split(r"\n(?=## \d{4}-\d{2}-\d{2}（)", text)
    return parts[-1] if len(parts) > 1 else ""


def subsection(section: str, name: str) -> str:
    match = re.search(r"^### " + re.escape(name) + r"[^\n]*\n(.*?)(?=^### |\Z)", section, re.S | re.M)
    return match.group(1).strip() if match else ""


def history(snapshots: list[dict]) -> list[dict]:
    rows = []
    prev = None
    for snap in sorted(snapshots, key=lambda x: str(x.get("date", ""))):
        row = dict(date=snap.get("date"), weekStart=snap.get("week_start"), focusTotalMin=snap.get("focus_total_min"),
                   pmDistinct=snap.get("pm_distinct"), pmScore=snap.get("pm_score"), pmMax=snap.get("pm_max"),
                   am2Answered=snap.get("am2_answered"), am2Correct=snap.get("am2_correct"), ankiReviews=snap.get("anki_reviews"))
        if prev:
            def delta(key: str):
                a, b = snap.get(key), prev.get(key)
                return (a - b) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None
            row.update(focusWeekMin=delta("focus_total_min"), pmWeekQuestions=delta("pm_distinct"),
                       am2WeekAnswered=delta("am2_answered"), am2WeekCorrect=delta("am2_correct"), ankiWeekReviews=delta("anki_reviews"))
        rows.append(row)
        prev = snap
    return rows


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not LATEST.is_file():
        raise SystemExit("outputs/weekly/latest.json がありません。先に scripts/weekly_sc_review.py を実行してください。")
    data = json.loads(LATEST.read_text(encoding="utf-8"))
    section = latest_section(REVIEW_MD.read_text(encoding="utf-8")) if REVIEW_MD.is_file() else ""
    notes = {key: subsection(section, name) for key, name in NOTE_HEADINGS.items()}
    heading = re.match(r"## ([^\n]*)", section)
    snapshots = json.loads(SNAPSHOTS.read_text(encoding="utf-8")) if SNAPSHOTS.is_file() else []
    payload = dict(
        generatedAt=dt.datetime.now(JST).isoformat(timespec="minutes"),
        reviewHeading=heading.group(1) if heading else "",
        review=data,
        notes=notes,
        history=history(snapshots),
    )
    OUTPUT.write_text(
        "// 自動生成: scripts/publish_sc_weekly_review.py（週次レビューの公開用データ。答案本文・設問別の採点結果は含まない）\n"
        "window.SC_WEEKLY_REVIEW=" + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"[info] {OUTPUT.relative_to(ROOT)} を更新しました（対象週 {data.get('weekStart')}〜{data.get('weekEnd')}、"
          f"注記 {sum(1 for v in notes.values() if v)}/4 件）")


if __name__ == "__main__":
    main()
