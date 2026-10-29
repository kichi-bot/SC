#!/usr/bin/env python3
"""翌日の「最初の1ポモ」を first_pomo.txt に書く。

書いた内容は C:/stock の StockScCountdown（scripts/sc_countdown.bat）が送る
09:00 の LINE 通知の先頭に「今日の最初の1ポモ: …」として載る（15:00 の通知には載らない）。
狙いは休日の午前に最初の1ポモを始めること。前夜のうちに、朝いちで手を付ける軽い1つだけを決める。

対象日の決め方: 深夜5時より前に書いたら「今日」、それ以降は「明日」。--date / --today で上書きできる。

使い方:
  py -3 scripts/set_first_pomo.py Anki「SC重点」を1ポモ     # 明日の分
  py -3 scripts/set_first_pomo.py                            # 引数なしなら入力を求める
  py -3 scripts/set_first_pomo.py --date 2026-11-01 午後問3  # 日付を指定
  py -3 scripts/set_first_pomo.py --show                     # 今書いてある内容を表示
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "first_pomo.txt"
NIGHT_END_HOUR = 5  # この時刻より前は「前夜の続き」とみなし、今日の分として書く
HEADER = (
    "# 明日の最初の1ポモ（09:00 の LINE 通知に載る）。1行目が対象日、2行目以降が内容。\n"
    "# 書き方: py -3 C:\\SC\\scripts\\set_first_pomo.py 内容\n"
)
_DATE_LINE = re.compile(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$")


def target_date(now: datetime, explicit: date | None = None, today: bool = False) -> date:
    """対象日を決める。--date > --today > 深夜5時前なら今日、それ以外は明日。"""
    if explicit is not None:
        return explicit
    if today or now.hour < NIGHT_END_HOUR:
        return now.date()
    return now.date() + timedelta(days=1)


def render(target: date, text: str) -> str:
    return f"{HEADER}{target.isoformat()}\n{text.strip()}\n"


def write_first_pomo(path: Path, target: date, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(target, text), encoding="utf-8", newline="\n")


def read_first_pomo(path: Path) -> tuple[date | None, str]:
    """(対象日, 内容) を返す。ファイルがない・日付行がないときは (None, "")。"""
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError:
        return None, ""
    lines = [line.strip() for line in raw.splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    if not lines:
        return None, ""
    match = _DATE_LINE.match(lines[0])
    if not match:
        return None, ""
    try:
        target = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None, ""
    return target, " / ".join(lines[1:])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="翌日の「最初の1ポモ」を書く（09:00 の LINE 通知に載る）")
    parser.add_argument("text", nargs="*", help="最初の1ポモの内容（空なら入力を求める）")
    parser.add_argument("--date", type=date.fromisoformat, help="対象日（YYYY-MM-DD）")
    parser.add_argument("--today", action="store_true", help="明日ではなく今日の分として書く")
    parser.add_argument("--show", action="store_true", help="今書いてある内容を表示して終わる")
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH, help=f"書き込み先（既定: {DEFAULT_PATH}）")
    parser.add_argument("--now", type=datetime.fromisoformat, help="現在日時の上書き（検証用）")
    args = parser.parse_args(argv)

    if args.show:
        target, text = read_first_pomo(args.path)
        if target is None:
            print(f"未設定（{args.path}）")
        else:
            print(f"{target.isoformat()} の最初の1ポモ: {text}")
        return 0

    text = " ".join(args.text).strip()
    if not text:
        try:
            text = input("明日の最初の1ポモ（例: Anki 1ポモ）: ").strip()
        except EOFError:
            text = ""
    if not text:
        print("内容が空なので書きませんでした。", file=sys.stderr)
        return 1

    now = args.now or datetime.now()
    target = target_date(now, args.date, args.today)
    write_first_pomo(args.path, target, text)
    print(f"{target.month}/{target.day} の最初の1ポモ: {text}")
    print(f"→ {args.path}（09:00 の LINE 通知に載ります）")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    raise SystemExit(main())
