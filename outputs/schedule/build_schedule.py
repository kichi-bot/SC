# -*- coding: utf-8 -*-
"""SC試験 学習スケジュール生成 v2 (2026-09-07): .ics / markdown / JSON(登録用)
前提: 毎日 8:45 起床。平日(祝日含む) 9:30-21:00 勤務(会社まで5分)。風呂は朝。勉強は平日夜 22:00- と土日朝。"""
import json, datetime as dt

TZ = "Asia/Tokyo"
OUT = r"C:\SC\outputs\schedule"
START, END = "2026-09-07", "2026-11-22"   # 日課の繰り返し範囲

# ============ 日課（繰り返し） ============
# color: 8=グラファイト(仕事/通勤) 7=ピーコック(生活) 2=セージ(自由)
ROUTINE = [
 # 平日 月〜金
 dict(title="起床・風呂", byday="MO,TU,WE,TH,FR", st="08:45", en="09:00", color="7", desc="朝風呂派。15分でシャワー。"),
 dict(title="朝食", byday="MO,TU,WE,TH,FR", st="09:00", en="09:15", color="7", desc="食べながら Anki を10枚だけ。"),
 dict(title="身支度", byday="MO,TU,WE,TH,FR", st="09:15", en="09:30", color="7", desc="9:30 始業。"),
 dict(title="仕事", byday="MO,TU,WE,TH,FR", st="09:30", en="21:00", color="8", desc="祝日も勤務前提で入れてある。休みの日はこの枠を消して朝 9:30〜12:00 を勉強に使う。"),
 dict(title="帰宅・夕食", byday="MO,TU,WE,TH,FR", st="21:00", en="22:00", color="7", desc="22:00 までに机に座る。"),
 dict(title="自由時間（勉強は休み）", byday="FR", st="22:00", en="23:30", color="2", desc="金曜夜は勉強なし。週末の朝に備えて早めに寝る。"),
 dict(title="就寝準備", byday="MO,TU,WE,TH,FR", st="23:30", en="24:00", color="7", desc="24:00 就寝 → 8:45 起床（約8.5時間）。"),
 # 土日
 dict(title="起床・風呂", byday="SA,SU", st="08:45", en="09:00", color="7", desc="朝風呂。"),
 dict(title="朝食", byday="SA,SU", st="09:00", en="09:30", color="7", desc="9:30 から勉強開始。"),
 dict(title="昼食", byday="SA,SU", st="12:30", en="13:30", color="7", desc=""),
 dict(title="家事（掃除・洗濯・買い出し）", byday="SA,SU", st="13:30", en="15:30", color="7", desc="平日にできない分をまとめて。"),
 dict(title="筋トレ", byday="SA,SU", st="15:30", en="16:30", color="6", desc="毎週土日1時間。家事のあと、自由時間の前に。"),
 dict(title="自由時間", byday="SA,SU", st="16:30", en="19:00", color="2", desc="外出・休息。勉強の借金があればここで1時間だけ返す。"),
 dict(title="夕食", byday="SA,SU", st="19:00", en="20:00", color="7", desc=""),
 dict(title="就寝準備", byday="SA,SU", st="23:30", en="24:00", color="7", desc="日曜 23:00 は燃えるゴミ（既存予定）。"),
]

# ============ 勉強：平日の固定枠（月・木、繰り返し） ============
STUDY_R = [
 dict(title="【SC】科目A-2 誤答演習（45分）＋Anki（15分）＋06 音読（30分）", byday="MO", start="2026-09-07", until="2026-10-19", color="10",
      desc="過去問道場で科目A-2 の誤答114問から10〜15問（週テーマ：9/7週 SAML・TLS／9/14週 NW・DB／9/21週 PKI・証明書／9/28週 暗号／10/5週〜 直近回）→ Anki 10〜15分 → 06 の1章を音読。Focus To-Do で計測。"),
 dict(title="【SC】科目A-2 25問模試（40分）＋答え合わせ（20分）＋Anki（30分）", byday="TH", start="2026-09-10", until="2026-10-22", color="10",
      desc="過去問道場の模試モードで25問・40分（本番と同じ時間）→ 誤答をチェックして月曜の誤答演習に回す。目標 17/25。"),
 dict(title="【SC】科目B 仕組みドリル（Aリスト Anki・06 音読・P分類の見直し）", byday="MO", start="2026-10-26", until="2026-11-16", color="9",
      desc="§4.1 Aリスト18件の Anki → 06 の該当章を音読 → 直近の通し演習の誤答 P 分類を見直す。新しい問は解かない（週末の通し演習に温存）。"),
 dict(title="【SC】科目B 仕組みドリル（Aリスト Anki・06 音読・P分類の見直し）", byday="TH", start="2026-10-29", until="2026-11-19", color="9",
      desc="§4.1 Aリスト18件の Anki → 06 の該当章を音読 → 混同ペア（復号/復元、認証/認可 など）を口頭で説明。"),
]
ST_R = ("22:00", "23:30")

# ============ 勉強：個別（火・水・土・日） ============
# 火 22:00-23:30 = 科目B 解答（65分・紙なし）＋メモ整理
# 水 22:00-23:00 = 前日分の採点・講評照合・P分類（23:00 燃えるゴミ）
# 土 9:30-12:30 / 日 9:30-12:00
S = []
def s(date, st, en, title, desc, color="9"):
    S.append(dict(date=date, start=st, end=en, title=title, desc=desc, color=color))
def pair(tue, wed, name, solve_desc, grade_desc):
    s(tue, "22:00", "23:30", "【SC】科目B %s 解答（65分・紙なし）" % name, solve_desc)
    s(wed, "22:00", "23:00", "【SC】科目B %s 採点・講評照合・P分類" % name, grade_desc)

# W2 9/7-13 ---------------------------------------------------------
pair("2026-09-08", "2026-09-09", "R5秋 問4（委託・リスクアセスメント）",
     "PDF画面＋キーボード入力・紙なし。設問→根拠段落をメモに書いてから本文。65分で切る。",
     "採点アプリで採点 → 講評照合 → P0〜P12分類。客観欄（56%）の取りこぼしを確認。")
s("2026-09-12", "09:30", "12:30", "【SC】科目B R7春 問4（ASM・脆弱性管理）解答＋採点",
  "解答65分 → 採点・講評照合・P分類45分。残りで §4.1 Aリストを Anki 化（10枚）。")
s("2026-09-13", "09:30", "12:00", "【SC】科目B R7秋 問4（管理・委託）解答＋採点",
  "柱②（管理・委託・リスク・脆弱性管理）3問目。\n▶ ゲート 9/13：採点済み累計10問。")
# W3 9/14-20 --------------------------------------------------------
pair("2026-09-15", "2026-09-16", "R5秋 問1 解き直し（XSS）",
     "月曜の 06 §1・§12 音読を踏まえて解く。XSS 3類型・CSP を仕組みから答える。",
     "前回 2.5/50 → 目標 20% 以上。誤答は P0（仕組み）か P1〜P12 かを必ず分ける。")
s("2026-09-19", "09:30", "12:30", "【SC】科目B R6秋 問3 解き直し（Web・アクセスログ）解答＋採点",
  "客観欄（用語穴埋め・記号 約22点分）を落とさない。\n▶ ゲート：Web 2問とも 20% 以上。")
s("2026-09-20", "09:30", "12:00", "【SC】科目B R6春 問1（JWT・API認証）採点",
  "紙解き済み → 採点アプリに入力し直して採点・講評照合・P分類。残りで Anki。")
# W4 9/21-27 --------------------------------------------------------
pair("2026-09-22", "2026-09-23", "R6秋 問4（セッション固定・HTTPヘッダ）",
     "新制度サンプル問題の元ネタ。初見65分。",
     "採点・講評照合・P分類。Set-Cookie 属性・セッションID再発行の仕組みを説明できるか。")
s("2026-09-26", "09:30", "12:30", "【SC】科目B R7春 問2（CVSS/EPSS/KEV・SBOM）解答＋採点",
  "解答65分 → 採点・講評照合・P分類。")
s("2026-09-27", "09:30", "12:00", "【SC】予備・遅れ回収＋暗号テンプレ＋「選ばない判断」練習",
  "未消化があればここで回収。なければ R7秋問2・R5秋問2 の設問だけ読み「選ばない判断」練習（各10分）→ 06 §4 暗号テンプレ暗記。\n▶ ゲート 9/27：採点済み累計13問。")
# W5 9/28-10/4 ------------------------------------------------------
pair("2026-09-29", "2026-09-30", "R7春 問1 解き直し（管理・委託）",
     "柱②の2回目。前回の P 分類メモを先に読んでから解く。",
     "採点・講評照合。前回比で伸びた欄／伸びない欄を記録。")
s("2026-10-03", "09:30", "12:30", "【SC】科目B R6秋 問2（メール・DMARC）解答＋採点",
  "知識型。SPF/DKIM/DMARC の仕組みを説明できるまで。解答 → 採点 → P分類。")
s("2026-10-04", "09:30", "12:00", "【SC】仕組みドリル（Aリスト18件）＋科目A-2 PKI/証明書 誤答",
  "§4.1 Aリスト18件を Anki 化し口頭で説明テスト（90分）→ 科目A-2 PKI/証明書の誤答（40分）→ Anki。", "10")
# W6 10/5-11 --------------------------------------------------------
pair("2026-10-06", "2026-10-07", "R6春 問3（XSS・CSRF・SSRF）",
     "紙解き済み → 採点アプリに入力し直す形で65分。Web は「1問だけ選ぶ前提で50%」が目標。",
     "採点・講評照合・P分類。SSRF の防御（許可リスト・メタデータ遮断）を説明できるか。")
s("2026-10-10", "09:30", "12:30", "【SC】科目B R7春 問3（スマホアプリ）解答＋採点",
  "未演習。解答65分 → 採点・講評照合・P分類。")
s("2026-10-11", "09:30", "12:00", "【SC】科目A-2 直近回模試＋誤答復習",
  "直近3回分から25問×1セット（40分）→ 誤答復習 → Anki。\n▶ ゲート 10/11：A-2 17/25。採点済み累計16問。", "10")
# W7 10/12-18 -------------------------------------------------------
pair("2026-10-13", "2026-10-14", "R6秋 問1 解き直し（ログ・IR）＋R4秋Ⅱ問2 設問読み",
     "第3候補（IR/ログ）の保険。R6秋問1 を解き直し（65分）。",
     "採点・講評照合 → R4秋Ⅱ問2 は設問だけ読んで解答方針をメモ（20分）。")
s("2026-10-17", "09:30", "12:30", "【SC】06 音読＋科目A-2 総復習",
  "06（用語別解答テンプレート）全章音読（60分）→ 科目A-2 誤答114問のうち未消化分（120分）。", "10")
s("2026-10-18", "09:30", "12:00", "【SC】科目A-2 模試×2（40分×2）",
  "直近回2セット。2回とも 17/25 以上なら受験準備完了。誤答は当日中に Anki 化。", "10")
# W8 10/19-25 -------------------------------------------------------
s("2026-10-20", "22:00", "23:30", "【SC】科目A-2 直近回模試（40分）＋誤答つぶし", "受験4日前。模試1セット → 誤答を Anki。SAML・TLS・問25枠を重点。", "10")
s("2026-10-21", "22:00", "23:00", "【SC】科目A-2 Anki 総ざらい（60分）", "新しい問題は解かない。Anki の科目A-2 デッキを全部回す。", "10")
s("2026-10-24", "13:30", "15:30", "【SC】科目A-2 受験後：自己採点メモ＋午後は休み",
  "受験直後に覚えている範囲で出題分野をメモ（CBT は問題非公開）。午後は家事・休息。", "11")
s("2026-10-25", "09:30", "12:00", "【SC】予備・遅れ回収②＋06 §4 暗号テンプレ・混同ペア",
  "科目B 未消化分があればここで回収。なければ 06 §4 暗号テンプレ暗記＋混同ペア（復号/復元 など）。")
# W9 10/26-11/1 -----------------------------------------------------
pair("2026-10-27", "2026-10-28", "R5秋 問1 2回目（XSS）",
     "Web 3問は2回解く。前回の P 分類メモを読んでから65分。",
     "採点・講評照合。1回目との差分を記録。目標 50%。")
s("2026-10-31", "09:30", "12:30", "【SC】通し演習① R6春（150分・紙なし）",
  "9:30〜12:00 本番形式：最初の10分で4問の設問だけ読み、枠判定・客観欄数・図表数をメモ機能に3行 → 2問選択（未演習の問2/問4を含める）。12:00〜 自己採点開始。")
s("2026-11-01", "09:30", "12:00", "【SC】通し①の採点・復習",
  "講評照合 → P分類 → 時間配分の振り返り。\n▶ 目標：2問で40点。")
# W10 11/2-8 --------------------------------------------------------
pair("2026-11-03", "2026-11-04", "R6秋 問3 2回目（Web・アクセスログ）",
     "Web 2回目。客観欄を全部取るつもりで65分。",
     "採点・講評照合。1回目との差分を記録。")
s("2026-11-07", "09:30", "12:30", "【SC】通し演習② R7秋（150分・紙なし）",
  "未演習の問3を含む4問から2問選択。本番形式 → 12:00〜 自己採点開始。")
s("2026-11-08", "09:30", "12:00", "【SC】通し②の採点・復習【前期判定】",
  "▶ 11/8 判定：初見2問・150分・紙なしで合計50点以上 → 前期で科目B合格圏。未満 → 前期は「A-2確保＋科目B本番経験」、後期（2027/3/16〜28）を本命に切替。")
# W11 11/9-15 -------------------------------------------------------
pair("2026-11-10", "2026-11-11", "R5秋 問4 2回目（委託・リスク）",
     "管理系の2回目。客観欄56%を取り切る。",
     "採点・講評照合。記述欄の字数（26〜45字）と句読点を確認。")
s("2026-11-14", "09:30", "12:30", "【SC】通し演習③ R5秋（150分・紙なし）",
  "未演習の問3を含む。目標55点。")
s("2026-11-15", "09:30", "12:00", "【SC】通し③の採点＋Aリスト総点検・混同ペア",
  "採点・講評照合 → §4.1 Aリスト18件の総点検 → 混同ペア（復号/復元 など）の最終確認。")
# W12 11/16-21 ------------------------------------------------------
s("2026-11-17", "22:00", "23:30", "【SC】06 音読（全章）＋通し③の誤答見直し", "新しい問は解かない。06 を通しで音読 → 通し③の P 分類メモを見直す。")
s("2026-11-18", "22:00", "23:00", "【SC】03 §4 チェックリスト＋時間配分の再確認", "選択10分／各問65分／見直し10分。メモ機能に書く3行のフォーマットを決めておく。")
s("2026-11-20", "22:00", "23:00", "【SC】前日：03 §4 チェックリストのみ",
  "新しい問題は解かない。本人確認書類（顔写真付き原本）・会場アクセス・予約時刻を確認して早く寝る。", "5")

# ============ 終日（登録済み・変更なし。ics/md 用） ============
A = [
 dict(start="2026-10-06", end="2026-10-06", title="【SC】申込開始（〜10/24 17:00）A-1免除申請・A/B同時予約"),
 dict(start="2026-10-17", end="2026-10-27", title="【SC】科目A 実施期間（10/17〜10/27）"),
 dict(start="2026-10-24", end="2026-10-24", title="【SC】科目A-2 受験（予定）"),
 dict(start="2026-11-11", end="2026-11-23", title="【SC】科目B 実施期間（11/11〜11/23）"),
 dict(start="2026-11-21", end="2026-11-21", title="【SC】科目B 受験（予定）"),
]
BOOKING = dict(date="2026-10-06", start="12:00", end="12:30", title="【SC】試験申込・会場予約（昼休みに）")

# ============ 週次レビューによる上書き（overrides.json、定期タスク sc-weekly-review が書く） ============
# 形式: {"replace":[{"week","date","title_prefix","set":{...},"reason"}], "add":[{"week","date","start","end","title","desc","color","reason"}],
#        "remove":[{"week","date","title_prefix","reason"}]}   ※ 日付＋タイトル先頭一致。削除は removed フラグにして UID を保つ。
OVR_PATH = OUT + r"\overrides.json"
CHANGELOG = []
try:
    with open(OVR_PATH, encoding="utf-8") as _f:
        _ovr = json.load(_f)
except FileNotFoundError:
    _ovr = {}
def _hit(e, o):
    return not e.get("removed") and e["date"] == o["date"] and e["title"].startswith(o.get("title_prefix", ""))
for o in _ovr.get("remove", []):
    for e in S:
        if _hit(e, o):
            e["removed"] = True
            CHANGELOG.append((o.get("week", ""), "削除", o["date"], e["title"], o.get("reason", "")))
for o in _ovr.get("replace", []):
    for e in S:
        if _hit(e, o):
            before = "%s %s〜%s %s" % (e["date"], e["start"], e["end"], e["title"])
            for k in ("date", "start", "end", "title", "desc", "color"):
                if k in o.get("set", {}):
                    e[k] = o["set"][k]
            CHANGELOG.append((o.get("week", ""), "変更", e["date"], before + " → " + e["title"], o.get("reason", "")))
for o in _ovr.get("add", []):
    S.append(dict(date=o["date"], start=o["start"], end=o["end"], title=o["title"], desc=o.get("desc", ""), color=str(o.get("color", "9"))))
    CHANGELOG.append((o.get("week", ""), "追加", o["date"], o["title"], o.get("reason", "")))

# ---------------- helpers ----------------
WD = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}
def ics_dt(date, hm):
    if hm == "24:00":
        date = (dt.date.fromisoformat(date) + dt.timedelta(days=1)).isoformat(); hm = "00:00"
    return date.replace("-", "") + "T" + hm.replace(":", "") + "00"
def esc(t):
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
def until_utc(date):
    return (dt.datetime.fromisoformat(date + "T23:59:00") - dt.timedelta(hours=9)).strftime("%Y%m%dT%H%M%SZ")
def first_on(start, byday):
    d = dt.date.fromisoformat(start); days = [WD[x] for x in byday.split(",")]
    while d.weekday() not in days: d += dt.timedelta(days=1)
    return d.isoformat()
def hours(st, en):
    h1, m1 = map(int, st.split(":")); h2, m2 = map(int, en.split(":")); return (h2*60+m2-h1*60-m1)/60

# ---------------- ICS ----------------
lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//SC study v2//JP","CALSCALE:GREGORIAN","METHOD:PUBLISH",
 "X-WR-CALNAME:SC試験 学習スケジュール 2026",
 "BEGIN:VTIMEZONE","TZID:Asia/Tokyo","BEGIN:STANDARD","DTSTART:19700101T000000","TZOFFSETFROM:+0900","TZOFFSETTO:+0900","TZNAME:JST","END:STANDARD","END:VTIMEZONE"]
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
ALARM = ["BEGIN:VALARM","TRIGGER:-PT15M","ACTION:DISPLAY","DESCRIPTION:Reminder","END:VALARM"]
def vevent(uid, extra):
    return ["BEGIN:VEVENT", "UID:sc2026v2-%s@sc-study" % uid, "DTSTAMP:" + stamp] + extra + ["END:VEVENT"]
for i, e in enumerate(S):
    if e.get("removed"):
        continue
    lines += vevent("s%02d" % i, ["DTSTART;TZID=%s:%s" % (TZ, ics_dt(e["date"], e["start"])), "DTEND;TZID=%s:%s" % (TZ, ics_dt(e["date"], e["end"])),
        "SUMMARY:" + esc(e["title"]), "DESCRIPTION:" + esc(e["desc"])] + ALARM)
e = BOOKING
lines += vevent("bk", ["DTSTART;TZID=%s:%s" % (TZ, ics_dt(e["date"], e["start"])), "DTEND;TZID=%s:%s" % (TZ, ics_dt(e["date"], e["end"])), "SUMMARY:" + esc(e["title"])] + ALARM)
for i, e in enumerate(A):
    d2 = (dt.date.fromisoformat(e["end"]) + dt.timedelta(days=1)).strftime("%Y%m%d")
    lines += vevent("a%02d" % i, ["DTSTART;VALUE=DATE:" + e["start"].replace("-", ""), "DTEND;VALUE=DATE:" + d2, "SUMMARY:" + esc(e["title"]), "TRANSP:TRANSPARENT"])
for i, e in enumerate(STUDY_R):
    d0 = first_on(e["start"], e["byday"])
    lines += vevent("r%02d" % i, ["DTSTART;TZID=%s:%s" % (TZ, ics_dt(d0, ST_R[0])), "DTEND;TZID=%s:%s" % (TZ, ics_dt(d0, ST_R[1])),
        "RRULE:FREQ=WEEKLY;BYDAY=%s;UNTIL=%s" % (e["byday"], until_utc(e["until"])), "SUMMARY:" + esc(e["title"]), "DESCRIPTION:" + esc(e["desc"])] + ALARM)
for i, e in enumerate(ROUTINE):
    d0 = first_on(START, e["byday"])
    lines += vevent("d%02d" % i, ["DTSTART;TZID=%s:%s" % (TZ, ics_dt(d0, e["st"])), "DTEND;TZID=%s:%s" % (TZ, ics_dt(d0, e["en"])),
        "RRULE:FREQ=WEEKLY;BYDAY=%s;UNTIL=%s" % (e["byday"], until_utc(END)), "SUMMARY:" + esc(e["title"]), "DESCRIPTION:" + esc(e["desc"])])
lines.append("END:VCALENDAR")
with open(OUT + r"\SC_study_schedule_2026.ics", "w", encoding="utf-8", newline="\r\n") as f:
    f.write("\n".join(lines))

# ---------------- 週次集計 & markdown ----------------
weeks = {}
def wk(d):
    d = dt.date.fromisoformat(d); return d - dt.timedelta(days=d.weekday())
for e in S:
    if e["color"] in ("9", "10", "5") and not e.get("removed"):
        weeks.setdefault(wk(e["date"]), []).append((e["date"], e["start"], e["end"], e["title"], hours(e["start"], e["end"])))
for e in STUDY_R:
    d = dt.date.fromisoformat(e["start"]); until = dt.date.fromisoformat(e["until"]); days = [WD[x] for x in e["byday"].split(",")]
    while d <= until:
        if d.weekday() in days:
            weeks.setdefault(wk(d.isoformat()), []).append((d.isoformat(), ST_R[0], ST_R[1], e["title"], 1.5))
        d += dt.timedelta(days=1)
JW = "月火水木金土日"
md = ["# 10_学習スケジュール_20260906", "",
 "> **作成日**：2026-09-06（v2 改訂 2026-09-07、以降は毎週月曜 5:00 の週次レビューで更新。変更は §6）　**対象期間**：2026-09-07（月）〜 2026-11-21（土・科目B受験予定）",
 "> **前提**：毎日 8:45 起床、風呂は朝。平日（祝日含む）は 9:30〜21:00 勤務（会社まで5分）。科目A-1 は免除（2025年度 応用情報合格）。`09` §6 の必要時間 約61h（科目B 52h＋A-2 9h）を11週で確保する。",
 "> **登録先**：Google カレンダー（petitgodzilla@gmail.com）。新Outlook に同アカウントが追加済みで、Outlook の予定表に同期表示されることを 9/7 に確認済み。outlook.jp 側に入れたい場合は `outputs/schedule/SC_study_schedule_2026.ics` を「予定表の追加 → ファイルからアップロード」で取り込む。", "",
 "## 1. 1日のテンプレート", "",
 "### 平日（月〜金、祝日も同じ）", "",
 "| 時刻 | 内容 |", "|---|---|",
 "| 8:45〜9:00 | 起床・風呂（朝） |", "| 9:00〜9:15 | 朝食（Anki 10枚） |", "| 9:15〜9:30 | 身支度 |",
 "| 9:30〜21:00 | 仕事 |", "| 21:00〜22:00 | 帰宅・夕食 |",
 "| 22:00〜23:30 | **勉強**（月：A-2 誤答＋Anki＋06音読／火：科目B 解答／水：採点・講評照合 〜23:00／木：A-2 模試／金：休み） |",
 "| 23:00〜23:30 | 水曜のみ 燃えるゴミ（既存） |", "| 23:30〜24:00 | 就寝準備（24:00 就寝、8:45 起床） |", "",
 "### 土日", "",
 "| 時刻 | 内容 |", "|---|---|",
 "| 8:45〜9:00 | 起床・風呂（朝） |", "| 9:00〜9:30 | 朝食 |",
 "| 9:30〜12:30（日は〜12:00） | **勉強**（科目B 1問 or 通し演習／採点・復習） |",
 "| 12:30〜13:30 | 昼食 |", "| 13:30〜15:30 | 家事（掃除・洗濯・買い出し） |", "| 15:30〜16:30 | 筋トレ |", "| 16:30〜19:00 | 自由時間 |",
 "| 19:00〜20:00 | 夕食 |", "| 23:00〜23:30 | 日曜のみ 燃えるゴミ（既存） |", "| 23:30〜24:00 | 就寝準備 |", "",
 "勉強時間は **平日 月〜木 1.5h×4（水は1h）＋土 3h＋日 2.5h ＝ 週約11h**。必要ライン 5.5h/週 の2倍なので、平日夜を半分落としても間に合う設計。10/26 以降の月・木は A-2 から科目B 仕組みドリルに切り替わる。", "",
 "## 2. 週次カレンダー（勉強のみ）", ""]
total = 0
for w in sorted(weeks):
    items = sorted(weeks[w]); h = sum(x[4] for x in items); total += h
    md += ["### %s〜%s　計 %.1fh" % (w.strftime("%m/%d"), (w + dt.timedelta(days=6)).strftime("%m/%d"), h), "", "| 日 | 時刻 | 内容 |", "|---|---|---|"]
    for d, st, en, t, hh in items:
        dd = dt.date.fromisoformat(d)
        md.append("| %s(%s) | %s〜%s | %s |" % (dd.strftime("%m/%d"), JW[dd.weekday()], st, en, t.replace("【SC】", "")))
    md.append("")
md += ["**合計 約%.0fh**（`09` §6.2 の必要量 約61h に対し余裕 約%.0fh）" % (total, total - 61), "",
 "## 3. 節目（終日イベント）", "", "| 日付 | 内容 |", "|---|---|"]
for e in A:
    md.append("| %s%s | %s |" % (e["start"], "" if e["start"] == e["end"] else "〜" + e["end"], e["title"].replace("【SC】", "")))
md.append("| 2026-10-06 12:00 | 試験申込・会場予約（昼休みにスマホで15分。A-1免除申請、A-2 10/24・科目B 11/21 を同時予約） |")
GATES = [
 ("2026-09-13", "採点済み累計10問", "9/27 の予備枠で回収"),
 ("2026-09-19", "Web 2問（R5秋問1・R6秋問3）とも 20% 以上", "10/25 の予備枠を Web に振り替え"),
 ("2026-09-27", "採点済み累計13問", "10/4 の仕組みドリルを科目B に寄せる"),
 ("2026-10-11", "A-2 17/25、採点済み累計16問", "10/17・10/18 を A-2 に全振り"),
 ("2026-10-18", "A-2 模試 2回とも 17/25 以上", "受験日を 10/27 まで後ろ倒し"),
 ("2026-11-01", "通し① 2問で 40点", "—"),
 ("2026-11-08", "通し② 2問で 50点 → 前期本番", "前期は経験、後期（2027/3/16〜28）本命に切替"),
 ("2026-11-15", "通し③ 55点", "—"),
]
md += ["", "## 4. ゲート", "", "| 日付 | 判定 | 未達なら |", "|---|---|---|"]
for gd, gl, gf in GATES:
    _d = dt.date.fromisoformat(gd); _bold = gd == "2026-11-08"
    _day = "%d/%d" % (_d.month, _d.day)
    md.append("| %s | %s | %s |" % ("**%s**" % _day if _bold else _day, "**%s**" % gl if _bold else gl, gf))
md += ["",
 "## 5. 運用ルール", "",
 "- 学習は Focus To-Do で計測し、`docs/assets/sc_focus_todo_progress_data.js` に反映する。",
 "- 演習は **PDF画面＋キーボード入力＋紙なし**（`09` §8）。必ず採点アプリで採点して記録する。",
 "- 平日夜が潰れた日は無理に取り返さない。土日の「予備」枠（9/27・10/25）と自由時間で回収する。",
 "- 祝日（9/21・9/22・9/23・10/12・11/3・11/23）が休みなら「仕事」の予定を消し、9:00〜11:30 を科目B に充てる。",
 "- 10/6（火）10:00 申込開始。昼休みに A-2（10/24）と科目B（11/21）を同時予約し、A-1 免除を申請する。",
 "- 予定を動かすときはカレンダー上でドラッグする。ここに書いた内容が正で、カレンダーはそのコピー。",
 "- 週次の計画変更は `outputs/schedule/overrides.json` に書いて `build_schedule.py` を再実行する（毎週月曜 5:00 の定期タスクが行う）。", "",
 "## 6. 変更履歴（週次レビュー）", "",
 "| 週 | 操作 | 日付 | 内容 | 理由 |", "|---|---|---|---|---|"]
if CHANGELOG:
    for w, op, d, what, why in CHANGELOG:
        md.append("| %s | %s | %s | %s | %s |" % (w, op, d, what.replace("【SC】", "").replace("|", "／"), why.replace("|", "／")))
else:
    md.append("| — | — | — | 変更なし | — |")
md.append("")
with open(r"C:\SC\10_学習スケジュール_20260906.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md))

json.dump(dict(sessions=[e for e in S if not e.get("removed")], study_recurring=STUDY_R, routine=ROUTINE, allday=A), open(OUT + r"\events.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- ダッシュボード用の公開データ（計画だけ。実績は含まない） ----------------
_JST = dt.timezone(dt.timedelta(hours=9))
site = dict(
    generatedAt=dt.datetime.now(_JST).isoformat(timespec="minutes"),
    period=dict(start=START, end="2026-11-21"),
    template=dict(weekday="月〜木 22:00〜23:30（水は〜23:00）", weekend="土 9:30〜12:30／日 9:30〜12:00", weeklyHours=11),
    weeks=[dict(start=w.isoformat(), end=(w + dt.timedelta(days=6)).isoformat(), hours=sum(x[4] for x in weeks[w]),
                items=[dict(date=d, start=st, end=en, title=t.replace("【SC】", ""), hours=hh) for d, st, en, t, hh in sorted(weeks[w])])
           for w in sorted(weeks)],
    totalHours=total,
    gates=[dict(date=gd, label=gl, fallback=gf) for gd, gl, gf in GATES],
    milestones=[dict(start=e["start"], end=e["end"], title=e["title"].replace("【SC】", "")) for e in A]
               + [dict(start=BOOKING["date"], end=BOOKING["date"], title=BOOKING["title"].replace("【SC】", "") + " " + BOOKING["start"])],
    changelog=[dict(week=w, op=op, date=d, what=what.replace("【SC】", ""), reason=why) for w, op, d, what, why in CHANGELOG],
)
with open(r"C:\SC\docs\assets\sc_schedule_data.js", "w", encoding="utf-8") as f:
    f.write("// 自動生成: outputs/schedule/build_schedule.py（学習計画の公開用データ。実績は含まない）\nwindow.SC_SCHEDULE=" + json.dumps(site, ensure_ascii=False) + ";\n")
print("sessions=%d study_recurring=%d routine=%d total_study_hours=%.2f" % (len(S), len(STUDY_R), len(ROUTINE), total))
for w in sorted(weeks):
    print(w, "%.2fh" % sum(x[4] for x in weeks[w]))
