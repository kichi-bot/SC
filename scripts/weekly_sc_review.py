# -*- coding: utf-8 -*-
"""SC 学習の週次レビュー集計（毎週月曜 5:00 の定期タスク sc-weekly-review から実行する）。

入力（すべてローカル・読み取りのみ）:
  - docs/assets/sc_pm_progress_data.js / sc_am2_progress_data.js /
    sc_focus_todo_progress_data.js / sc_anki_progress_data.js
    （Codex の自動化「SC 3サイト進捗同期」が毎日 4:00 に更新する公開用集計）
  - %USERPROFILE%\\Downloads\\sc_pm_public_progress*.json
    （採点アプリの公開用集計。問ごとの score/max/gradedAt だけで、答案本文は含まない）
  - outputs/schedule/events.json（build_schedule.py が生成する学習計画）
出力:
  - 標準出力に markdown（先週の計画×実績、累計、ゲート判定、データ鮮度、次週の計画）
  - --append で 11_週次レビュー.md の末尾に同じ内容を追記（同じ日の再実行はその日のセクションを作り直す）
  - outputs/weekly/latest.json（集計値。publish_sc_weekly_review.py がダッシュボード用JSにする）
  - outputs/weekly/calendar_actuals.json（Google カレンダーへ実績を反映するための指示書）
  - outputs/weekly/snapshots.json に週次スナップショット（Focus To-Do の累計差分用）

使い方:
  py -3 scripts/weekly_sc_review.py                 # 表示のみ（latest.json 等は更新、スナップショットも保存）
  py -3 scripts/weekly_sc_review.py --append        # 11_週次レビュー.md に追記
  py -3 scripts/weekly_sc_review.py --week-start 2026-08-31 --no-snapshot
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
EVENTS = ROOT / "outputs" / "schedule" / "events.json"
REVIEW_MD = ROOT / "11_週次レビュー.md"
WEEKLY_DIR = ROOT / "outputs" / "weekly"
SNAPSHOTS = WEEKLY_DIR / "snapshots.json"
LATEST = WEEKLY_DIR / "latest.json"
CAL_ACTUALS = WEEKLY_DIR / "calendar_actuals.json"
DOWNLOADS = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Downloads"
JST = dt.timezone(dt.timedelta(hours=9))
JW = "月火水木金土日"
WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
ST_R = ("22:00", "23:30")  # build_schedule.py の月・木固定枠と同じ
STUDY_COLORS = {"9", "10", "5", "11"}

# 10_学習スケジュール §4 のゲート（判定はこのスクリプトで機械的に行う）
GATES = [
    ("2026-09-13", "採点済み累計10問", "pm_distinct", 10),
    ("2026-09-19", "Web 2問（R5秋問1・R6秋問3）とも 20% 以上", "web2", 20.0),
    ("2026-09-27", "採点済み累計13問", "pm_distinct", 13),
    ("2026-10-11", "A-2 直近模試 17/25（68%）・採点済み累計16問", "am2_and_pm", (68.0, 16)),
    ("2026-10-18", "A-2 模試 2回連続 17/25 以上", "am2_two", 68.0),
    ("2026-11-01", "通し① R6春 2問で40点", "mock", ("令和6年春期", 40.0)),
    ("2026-11-08", "通し② R7秋 2問で50点（前期本番の判定）", "mock", ("令和7年秋期", 50.0)),
    ("2026-11-15", "通し③ R5秋 2問で55点", "mock", ("令和5年秋期", 55.0)),
]


# ---------------- 読み込み ----------------
def load_js(path: Path, var: str) -> dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    match = re.search(r"window\." + re.escape(var) + r"=(\{.*\});\s*$", text, re.S)
    return json.loads(match.group(1)) if match else {}


def parse_ts(value: object) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=JST)
    return parsed.astimezone(JST)


def load_exports(downloads: Path) -> list[dict]:
    """採点アプリの公開用集計JSONを全部読み、試験回×問×演習回ごとに最新の採点結果だけ残す。"""
    records: dict[tuple[str, str, int], dict] = {}
    files = sorted(downloads.glob("sc_pm_public_progress*.json"), key=lambda p: p.stat().st_mtime)
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        version = payload.get("schemaVersion")
        if version not in (1, 2) or not isinstance(payload.get("questions"), list):
            continue
        for item in payload["questions"]:
            try:
                exam, question = str(item["exam"]), str(item["question"])
                score, maximum = float(item["score"]), float(item["max"])
                attempt = int(item.get("attempt", 1)) if version == 2 else 1
            except (KeyError, TypeError, ValueError):
                continue
            graded = parse_ts(item.get("gradedAt"))
            if graded is None or maximum <= 0 or attempt < 1:
                continue
            key = (exam, question, attempt)
            if key not in records or records[key]["gradedAt"] < graded:
                records[key] = dict(exam=exam, question=question, attempt=attempt, score=score, max=maximum, gradedAt=graded)
    return list(records.values())


def latest_attempts(records: list[dict]) -> dict[tuple[str, str], dict]:
    latest: dict[tuple[str, str], dict] = {}
    for rec in records:
        key = (rec["exam"], rec["question"])
        if key not in latest or latest[key]["gradedAt"] < rec["gradedAt"]:
            latest[key] = rec
    return latest


def parse_day(label: object) -> dt.date | None:
    if isinstance(label, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", label):
        return dt.date.fromisoformat(label)
    return None


# ---------------- 計画 ----------------
def hours(start: str, end: str) -> float:
    h1, m1 = map(int, start.split(":"))
    h2, m2 = map(int, end.split(":"))
    return ((h2 * 60 + m2) - (h1 * 60 + m1)) / 60


def planned_sessions(events: dict, day0: dt.date, day1: dt.date) -> list[dict]:
    out = []
    for item in events.get("sessions", []):
        if item.get("removed"):
            continue
        day = dt.date.fromisoformat(item["date"])
        if day0 <= day <= day1 and str(item.get("color", "9")) in STUDY_COLORS:
            out.append(dict(date=day, start=item["start"], end=item["end"], title=item["title"], hours=hours(item["start"], item["end"]), recurring=False))
    for item in events.get("study_recurring", []):
        days = [WD[x] for x in item["byday"].split(",")]
        first, until = dt.date.fromisoformat(item["start"]), dt.date.fromisoformat(item["until"])
        day = max(day0, first)
        while day <= min(day1, until):
            if day.weekday() in days:
                out.append(dict(date=day, start=ST_R[0], end=ST_R[1], title=item["title"], hours=hours(*ST_R), recurring=True))
            day += dt.timedelta(days=1)
    return sorted(out, key=lambda x: (x["date"], x["start"]))


EXAM_RE = re.compile(r"R(\d)(春|秋)\s*(Ⅰ|Ⅱ|I{1,2})?\s*問(\d)")


def session_target(title: str) -> tuple[str, str] | None:
    """計画タイトルから（試験回ラベル, 問ラベル）を取り出す。例: 'R5秋 問4' -> ('令和5年秋期', '問4')"""
    match = EXAM_RE.search(title)
    if not match:
        return None
    year, season, part, number = match.groups()
    exam = f"令和{year}年{'春期' if season == '春' else '秋期'}"
    question = f"問{number}"
    if part in ("Ⅱ", "II"):
        question = f"午後Ⅱ 問{number}"
    elif part in ("Ⅰ", "I"):
        question = f"午後Ⅰ 問{number}"
    return exam, question


def question_matches(record_question: str, wanted: str) -> bool:
    if record_question == wanted:
        return True
    if wanted.startswith("午後"):
        return wanted.replace(" ", "") in record_question.replace(" ", "")
    return record_question.replace(" ", "").endswith(wanted)


def dlabel(day: dt.date) -> str:
    return f"{day.strftime('%m/%d')}({JW[day.weekday()]})"


# ---------------- 集計 ----------------
def in_window(day: dt.date, day0: dt.date, day1: dt.date) -> bool:
    return day0 <= day <= day1


def collect(week_start: dt.date, today: dt.date, snapshots: list[dict]) -> dict:
    week_end = week_start + dt.timedelta(days=6)
    next_start, next_end = week_end + dt.timedelta(days=1), week_end + dt.timedelta(days=7)
    now = dt.datetime.now(JST)

    pm = load_js(ASSETS / "sc_pm_progress_data.js", "SC_PM_PROGRESS")
    am2 = load_js(ASSETS / "sc_am2_progress_data.js", "SC_AM2_PROGRESS")
    focus = load_js(ASSETS / "sc_focus_todo_progress_data.js", "SC_FOCUS_TODO_PROGRESS")
    anki = load_js(ASSETS / "sc_anki_progress_data.js", "SC_ANKI_PROGRESS")
    events = json.loads(EVENTS.read_text(encoding="utf-8")) if EVENTS.is_file() else {}
    records = load_exports(DOWNLOADS)
    latest = latest_attempts(records)

    # --- 先週の実績 ---
    week_records = [r for r in records if in_window(r["gradedAt"].date(), week_start, week_end)]
    pm_week_score = sum(r["score"] for r in week_records)
    pm_week_max = sum(r["max"] for r in week_records)
    pm_week_n: int | None = len(week_records)
    if not records:  # 公開用集計JSONが無い場合は公開データの日別集計で代用
        pm_week_n = None
        for day in pm.get("days", []):
            d = parse_day(day.get("label"))
            if d and in_window(d, week_start, week_end):
                pm_week_score += float(day.get("score", 0))
                pm_week_max += float(day.get("max", 0))
                pm_week_n = (pm_week_n or 0) + int(day.get("questions", 0))
    am2_week_total = am2_week_correct = 0
    am2_days: dict[dt.date, dict] = {}
    for day in am2.get("days", []):
        d = parse_day(day.get("label"))
        if not d:
            continue
        am2_days[d] = day
        if in_window(d, week_start, week_end):
            am2_week_total += int(day.get("total", 0))
            am2_week_correct += int(day.get("correct", 0))
    anki_week_reviews = anki_week_minutes = 0
    anki_days: dict[dt.date, dict] = {}
    for day in anki.get("days", []):
        d = parse_day(day.get("label"))
        if not d:
            continue
        anki_days[d] = day
        if in_window(d, week_start, week_end):
            anki_week_reviews += int(day.get("reviews", 0))
            anki_week_minutes += int(day.get("minutes", 0))

    focus_total = focus.get("totalMinutes")
    focus_captured = parse_ts(focus.get("capturedAt"))
    prev = None
    for snap in snapshots:
        snap_day = parse_day(snap.get("date"))
        if snap_day and snap_day < today:
            prev = snap
    focus_delta = None
    if prev and isinstance(focus_total, (int, float)) and isinstance(prev.get("focus_total_min"), (int, float)):
        prev_captured = parse_ts(prev.get("focus_captured_at"))
        if focus_captured and prev_captured and focus_captured > prev_captured:
            focus_delta = focus_total - prev["focus_total_min"]

    # --- 累計 ---
    pm_distinct = len(latest) if latest else sum(len(m.get("completed", [])) for m in pm.get("questionMaps", []))
    pm_total_score = sum(r["score"] for r in latest.values()) if latest else float(pm.get("score", 0))
    pm_total_max = sum(r["max"] for r in latest.values()) if latest else float(pm.get("max", 0))
    pm_accuracy = round(pm_total_score / pm_total_max * 100, 1) if pm_total_max else 0.0
    am2_answered, am2_correct = int(am2.get("answered", 0)), int(am2.get("correct", 0))
    recent_days = sorted(am2.get("days", []), key=lambda d: str(d.get("label", "")), reverse=True)
    recent_total = recent_correct = 0
    for day in recent_days:
        recent_total += int(day.get("total", 0))
        recent_correct += int(day.get("correct", 0))
        if recent_total >= 50:
            break
    recent_acc = round(recent_correct / recent_total * 100, 1) if recent_total else None

    # --- ゲート判定 ---
    def score_pct(exam: str, question: str) -> float | None:
        for (ex, q), rec in latest.items():
            if ex == exam and question_matches(q, question):
                return round(rec["score"] / rec["max"] * 100, 1)
        return None

    def mock_score(exam: str, gate_day: dt.date) -> float | None:
        window0 = gate_day - dt.timedelta(days=2)
        hits = [r for r in records if r["exam"] == exam and in_window(r["gradedAt"].date(), window0, gate_day)]
        if not hits:
            return None
        best: dict[str, dict] = {}
        for r in hits:
            if r["question"] not in best or best[r["question"]]["gradedAt"] < r["gradedAt"]:
                best[r["question"]] = r
        return sum(r["score"] for r in best.values())

    gate_rows = []
    for gate_date, label, kind, threshold in GATES:
        g = dt.date.fromisoformat(gate_date)
        if g > today + dt.timedelta(days=7):
            continue
        status, value = "判定不能", "—"
        if kind == "pm_distinct":
            value = f"{pm_distinct}問"
            status = "達成" if pm_distinct >= threshold else "未達"
        elif kind == "web2":
            a, b = score_pct("令和5年秋期", "問1"), score_pct("令和6年秋期", "問3")
            value = f"R5秋問1 {a if a is not None else '未'}% / R6秋問3 {b if b is not None else '未'}%"
            if a is not None and b is not None:
                status = "達成" if min(a, b) >= threshold else "未達"
        elif kind == "am2_and_pm":
            acc_th, pm_th = threshold
            value = f"A-2 直近{recent_total}問 {recent_acc if recent_acc is not None else '—'}% / 採点済み {pm_distinct}問"
            if recent_acc is not None:
                status = "達成(推定)" if recent_acc >= acc_th and pm_distinct >= pm_th else "未達"
        elif kind == "am2_two":
            two = [d for d in recent_days if int(d.get("total", 0)) >= 20][:2]
            value = " / ".join(f"{d['label']} {d.get('accuracy', '—')}%" for d in two) or "模試2回分の記録なし"
            if len(two) == 2:
                status = "達成(推定)" if all(float(d.get("accuracy", 0)) >= threshold for d in two) else "未達"
        elif kind == "mock":
            exam, need = threshold
            got = mock_score(exam, g)
            value = f"{got:.1f}点" if got is not None else "採点記録なし"
            if got is not None:
                status = "達成" if got >= need else "未達"
        if g > today:
            status = "次のゲート（" + status + "）" if status != "判定不能" else "次のゲート"
        gate_rows.append(dict(date=gate_date, label=label, value=value, status=status))

    # --- 先週の計画×実績 ---
    plan_rows = []
    done = 0
    for s in planned_sessions(events, week_start, week_end):
        target = session_target(s["title"])
        evidence, status = "—", "unknown"
        if target:
            exam, question = target
            hits = [r for r in week_records if r["exam"] == exam and question_matches(r["question"], question)]
            if hits:
                best = max(hits, key=lambda r: r["gradedAt"])
                evidence = f"採点 {best['score']:g}/{best['max']:g}点（{best['score'] / best['max'] * 100:.0f}%）"
                status = "done"
            else:
                evidence, status = "採点記録なし", "none"
        elif "A-2" in s["title"] or "科目A" in s["title"]:
            day = am2_days.get(s["date"])
            if day:
                evidence, status = f"過去問道場 {day.get('total')}問 {day.get('accuracy')}%", "done"
            else:
                evidence, status = "過去問道場の記録なし", "none"
        elif any(k in s["title"] for k in ("Anki", "ドリル", "音読")):
            day = anki_days.get(s["date"])
            if day:
                evidence, status = f"Anki {day.get('reviews')}回 {day.get('minutes')}分", "done"
            else:
                evidence, status = "Anki の記録なし", "none"
        if status == "done":
            done += 1
        plan_rows.append(dict(date=s["date"].isoformat(), start=s["start"], end=s["end"], title=s["title"], hours=s["hours"],
                              recurring=s["recurring"], status=status, evidence=evidence))
    planned_hours = sum(r["hours"] for r in plan_rows)

    # --- データ鮮度 ---
    def age_row(name: str, ts: dt.datetime | None, note: str) -> dict:
        if ts is None:
            return dict(name=name, when="不明", ageDays=None, judge="要更新", note=note)
        days = (now - ts).days
        judge = "OK" if days <= 2 else ("注意" if days <= 6 else "要更新")
        return dict(name=name, when=ts.strftime("%m/%d %H:%M"), ageDays=days, judge=judge, note=note)

    fresh_rows = [
        age_row("科目B 採点（sc_pm_progress_data.js）", parse_ts(pm.get("exportedAt")), "最終採点日 " + str(pm.get("lastStudyDate", "—"))),
        age_row("採点アプリ公開用集計JSON（Downloads）", max((r["gradedAt"] for r in records), default=None), "採点した日の最新"),
        age_row("科目A-2 過去問道場（sc_am2_progress_data.js）", parse_ts(am2.get("downloadedAt")), "最終学習日 " + str(am2.get("lastStudyDate", "—")) + "。更新は4:00のCodex自動化（道場ログイン要）"),
        age_row("Focus To-Do（sc_focus_todo_progress_data.js）", focus_captured, "更新は4:00のCodex自動化（アプリ表示要）"),
        age_row("Anki（sc_anki_progress_data.js）", parse_ts(anki.get("capturedAt")), "update_sc_anki_progress.py で更新可"),
    ]

    # --- 次週の計画 ---
    next_rows = [dict(date=s["date"].isoformat(), start=s["start"], end=s["end"], title=s["title"], hours=s["hours"], recurring=s["recurring"])
                 for s in planned_sessions(events, next_start, next_end)]

    return dict(
        generatedAt=now.isoformat(timespec="minutes"),
        today=today.isoformat(), weekStart=week_start.isoformat(), weekEnd=week_end.isoformat(),
        nextStart=next_start.isoformat(), nextEnd=next_end.isoformat(),
        summary=dict(
            focus=dict(weekMinutes=focus_delta, totalMinutes=focus_total, monthMinutes=focus.get("monthMinutes"), capturedAt=focus.get("capturedAt"),
                       previousSnapshot=(prev or {}).get("date")),
            pm=dict(weekQuestions=pm_week_n, weekScore=pm_week_score, weekMax=pm_week_max, distinct=pm_distinct,
                    score=pm_total_score, max=pm_total_max, accuracy=pm_accuracy, lastStudyDate=pm.get("lastStudyDate"),
                    source="export" if records else "public"),
            am2=dict(weekTotal=am2_week_total, weekCorrect=am2_week_correct, answered=am2_answered, correct=am2_correct,
                     accuracy=am2.get("accuracy"), recentTotal=recent_total, recentAccuracy=recent_acc, lastStudyDate=am2.get("lastStudyDate")),
            anki=dict(weekReviews=anki_week_reviews, weekMinutes=anki_week_minutes, reviews=anki.get("reviews"),
                      totalCards=anki.get("totalCards"), lastStudyDate=anki.get("lastStudyDate")),
        ),
        planActual=plan_rows, plannedHours=planned_hours, doneCount=done,
        gates=gate_rows, freshness=fresh_rows,
        nextWeek=next_rows, nextHours=sum(r["hours"] for r in next_rows),
    )


def render_markdown(data: dict) -> str:
    s = data["summary"]
    ws, we = dt.date.fromisoformat(data["weekStart"]), dt.date.fromisoformat(data["weekEnd"])
    ns, ne = dt.date.fromisoformat(data["nextStart"]), dt.date.fromisoformat(data["nextEnd"])
    today = dt.date.fromisoformat(data["today"])
    f, p, a, k = s["focus"], s["pm"], s["am2"], s["anki"]
    focus_week = "未取得（前週スナップショットなし）" if f["weekMinutes"] is None else f"{f['weekMinutes'] / 60:.1f}h"
    focus_total = "—" if f["totalMinutes"] is None else f"{f['totalMinutes'] / 60:.1f}h"
    pm_week = f"{p['weekQuestions'] if p['weekQuestions'] is not None else '—'}問 {p['weekScore']:g}/{p['weekMax']:g}点"
    lines = [
        f"## {today.isoformat()}（{JW[today.weekday()]}）レビュー：対象週 {dlabel(ws)}〜{dlabel(we)}",
        "",
        "### 実績サマリ",
        "",
        "| 指標 | 先週 | 累計 |",
        "|---|---|---|",
        f"| 学習時間（Focus To-Do） | {focus_week} | {focus_total}（当月 {f['monthMinutes'] if f['monthMinutes'] is not None else '—'}分） |",
        f"| 科目B 採点 | {pm_week} | {p['distinct']}問 {p['score']:g}/{p['max']:g}点（{p['accuracy']}%） |",
        f"| 科目A-2 過去問道場 | {a['weekTotal']}問 正答{a['weekCorrect']} | {a['answered']}問 {a['accuracy'] if a['accuracy'] is not None else '—'}%（直近{a['recentTotal']}問 {a['recentAccuracy'] if a['recentAccuracy'] is not None else '—'}%） |",
        f"| Anki | {k['weekReviews']}回 {k['weekMinutes']}分 | {k['reviews'] if k['reviews'] is not None else '—'}回 / {k['totalCards'] if k['totalCards'] is not None else '—'}枚 |",
        "",
        f"### 先週の計画×実績（計画 {data['plannedHours']:.1f}h・{len(data['planActual'])}枠、実施の痕跡あり {data['doneCount']}枠）",
        "",
        "| 日 | 時刻 | 計画 | 実績の痕跡 |",
        "|---|---|---|---|",
    ]
    for r in data["planActual"]:
        lines.append(f"| {dlabel(dt.date.fromisoformat(r['date']))} | {r['start']}〜{r['end']} | {r['title'].replace('【SC】', '')} | {r['evidence']} |")
    if not data["planActual"]:
        lines.append("| — | — | 計画なし | — |")
    lines += ["", "> 痕跡は「採点記録・過去問道場の学習日・Ankiの学習日」から機械的に判定。音読や紙上の作業は検出できないので、未検出＝未実施ではない。", "",
              "### ゲート判定", "", "| 期限 | 判定 | 現在値 | 結果 |", "|---|---|---|---|"]
    for g in data["gates"]:
        lines.append(f"| {g['date']} | {g['label']} | {g['value']} | {g['status']} |")
    if not data["gates"]:
        lines.append("| — | 直近1週間にゲートなし | — | — |")
    lines += ["", "### データ鮮度", "", "| データ | 最終更新 | 判定 |", "|---|---|---|"]
    for r in data["freshness"]:
        age = f"（{r['ageDays']}日前）" if r["ageDays"] is not None else ""
        lines.append(f"| {r['name']} | {r['when']}{age} | {r['judge']}。{r['note']} |")
    lines += ["", f"### 次週の計画（{dlabel(ns)}〜{dlabel(ne)}、計 {data['nextHours']:.1f}h）", "", "| 日 | 時刻 | 内容 |", "|---|---|---|"]
    for r in data["nextWeek"]:
        lines.append(f"| {dlabel(dt.date.fromisoformat(r['date']))} | {r['start']}〜{r['end']} | {r['title'].replace('【SC】', '')} |")
    if not data["nextWeek"]:
        lines.append("| — | — | 計画なし |")
    lines.append("")
    return "\n".join(lines)


def calendar_actuals(data: dict) -> dict:
    """Google カレンダーへ実績を書き戻すための指示書（定期タスクがこれを読んで update/create する）。"""
    s = data["summary"]
    f, p, a, k = s["focus"], s["pm"], s["am2"], s["anki"]
    parts = [
        "学習 " + (f"{f['weekMinutes'] / 60:.1f}h" if f["weekMinutes"] is not None else "—"),
        (f"科目B {p['weekQuestions']}問 {p['weekScore']:g}/{p['weekMax']:g}点" if p["weekQuestions"] else "科目B 採点なし"),
        (f"道場 {a['weekTotal']}問 {round(a['weekCorrect'] / a['weekTotal'] * 100)}%" if a["weekTotal"] else "道場 0問"),
        f"Anki {k['weekReviews']}回",
    ]
    ws, we = dt.date.fromisoformat(data["weekStart"]), dt.date.fromisoformat(data["weekEnd"])
    description = "\n".join([
        f"対象週 {dlabel(ws)}〜{dlabel(we)}（毎週月曜 5:00 の自動集計）",
        f"学習時間（Focus To-Do）：{parts[0][3:]}（累計 {f['totalMinutes'] / 60:.1f}h）" if f["totalMinutes"] is not None else "学習時間（Focus To-Do）：未取得",
        f"科目B：先週 {parts[1][4:]}／累計 {p['distinct']}問 {p['score']:g}/{p['max']:g}点（{p['accuracy']}%）",
        f"科目A-2 過去問道場：先週 {a['weekTotal']}問 正答{a['weekCorrect']}／累計 {a['answered']}問 {a['accuracy']}%（直近{a['recentTotal']}問 {a['recentAccuracy']}%）",
        f"Anki：先週 {k['weekReviews']}回 {k['weekMinutes']}分",
        "計画の実施痕跡：%d/%d 枠" % (data["doneCount"], len(data["planActual"])),
        "詳細は C:\\SC\\11_週次レビュー.md",
    ])
    sessions = []
    for r in data["planActual"]:
        sessions.append(dict(date=r["date"], start=r["start"], end=r["end"], title=r["title"], recurring=r["recurring"], status=r["status"],
                             prefix={"done": "✅ ", "none": "⬜ "}.get(r["status"], ""),
                             resultLine=("【実績】" + r["evidence"]) if r["status"] != "unknown" else ""))
    return dict(
        generatedAt=data["generatedAt"], weekStart=data["weekStart"], weekEnd=data["weekEnd"],
        rules=[
            "対象は先週（weekStart〜weekEnd）の、タイトルが【SC】で始まる予定だけ。日付＋タイトル先頭一致（既存の ✅/⬜ 接頭辞は外して比較）。",
            "status=done → summary を prefix+元タイトル に、description の先頭行を resultLine に置き換える（既に【実績】行があれば差し替え）。",
            "status=none → prefix を ⬜ にし、resultLine を先頭行にする。status=unknown → 触らない。",
            "月・木の繰り返し予定はそのインスタンス（id が _YYYYMMDD… で終わる）だけを更新し、繰り返し本体は触らない。",
            "weeklySummary は weekEnd（日曜）の終日予定として作成。同じ日に【SC実績】で始まる終日予定があれば更新する。colorId 3、availability FREE。",
            "開始・終了時刻は変えない。【SC】以外の予定は触らない。",
        ],
        sessions=sessions,
        weeklySummary=dict(date=data["weekEnd"], title="【SC実績】" + "・".join(parts), description=description, colorId="3"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="SC 学習の週次レビュー集計")
    parser.add_argument("--week-start", help="対象週の月曜（YYYY-MM-DD）。省略時は直前に終わった週（月〜日）")
    parser.add_argument("--today", help="実行日として扱う日付（テスト用）")
    parser.add_argument("--append", action="store_true", help="11_週次レビュー.md に追記する")
    parser.add_argument("--no-snapshot", action="store_true", help="スナップショットを保存しない")
    args = parser.parse_args()

    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(JST).date()
    if args.week_start:
        week_start = dt.date.fromisoformat(args.week_start)
    else:
        # 直前に終わった週（月〜日）を対象にする。月曜 5:00 の定期実行が遅れて火曜以降に走っても同じ週を見る。
        this_monday = today - dt.timedelta(days=today.weekday())
        week_start = this_monday - dt.timedelta(days=7)
    snapshots = json.loads(SNAPSHOTS.read_text(encoding="utf-8")) if SNAPSHOTS.is_file() else []

    data = collect(week_start, today, snapshots)
    markdown = render_markdown(data)
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    LATEST.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    CAL_ACTUALS.write_text(json.dumps(calendar_actuals(data), ensure_ascii=False, indent=1), encoding="utf-8")
    if not args.no_snapshot:
        s = data["summary"]
        snapshot = dict(
            date=today.isoformat(), week_start=week_start.isoformat(),
            focus_total_min=s["focus"]["totalMinutes"], focus_captured_at=s["focus"]["capturedAt"],
            pm_distinct=s["pm"]["distinct"], pm_score=s["pm"]["score"], pm_max=s["pm"]["max"],
            am2_answered=s["am2"]["answered"], am2_correct=s["am2"]["correct"],
            anki_reviews=s["anki"]["reviews"],
        )
        others = [x for x in snapshots if x.get("date") != today.isoformat()]
        SNAPSHOTS.write_text(json.dumps(others + [snapshot], ensure_ascii=False, indent=1), encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8")
    print(markdown)
    if args.append:
        header = "# 11_週次レビュー\n\n> 毎週月曜 5:00 の定期タスク（sc-weekly-review）が `scripts/weekly_sc_review.py` で集計し、判断と変更を追記する。答案本文や設問別の採点結果は載せない。\n"
        existing = REVIEW_MD.read_text(encoding="utf-8") if REVIEW_MD.is_file() else header
        heading = f"## {today.isoformat()}（"
        if heading in existing:
            # 同じ日に再実行した場合は、その日のセクション（後から追記した判断も含む）を丸ごと作り直す
            start = existing.index(heading)
            sep = existing.rfind("\n---\n", 0, start)
            start = sep if sep != -1 else start
            nxt = existing.find("\n---\n\n## ", start + 1)
            existing = existing[:start] + (existing[nxt:] if nxt != -1 else "")
            print(f"[info] {REVIEW_MD.name} の {today.isoformat()} セクションを作り直します。", file=sys.stderr)
        REVIEW_MD.write_text(existing.rstrip("\n") + "\n\n---\n\n" + markdown, encoding="utf-8")
        print(f"[info] {REVIEW_MD.name} に追記しました。", file=sys.stderr)


if __name__ == "__main__":
    main()
