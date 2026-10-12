# -*- coding: utf-8 -*-
"""SC試験 学習スケジュール生成 v3 (2026-10-06 受験日確定で再編): .ics / markdown / JSON(登録用)
前提: 毎日 8:45 起床。平日(祝日含む) 9:30-21:00 勤務(会社まで5分)。風呂は朝。
v3: 受験日 科目A-2 10/27(火)17:15 金山 / 科目B 11/23(月祝)15:30 名駅。
    Focus To-Do の実績(土日朝枠は8週ゼロ・平日夜は Anki 50分のみ)に合わせ、勉強は土日の午後(14:00-)と平日夜の1ユニット(22:00-22:50)。"""
import json, datetime as dt

TZ = "Asia/Tokyo"
OUT = r"C:\SC\outputs\schedule"
START, END = "2026-09-07", "2026-11-22"   # 日課の繰り返し範囲（11/23 は受験日。日課なし）
PERIOD_END = "2026-11-23"

# ============ 日課（繰り返し） ============
# color: 8=グラファイト(仕事/通勤) 7=ピーコック(生活) 2=セージ(自由)
ROUTINE = [
 # 平日 月〜金
 dict(title="起床・風呂", byday="MO,TU,WE,TH,FR", st="08:45", en="09:00", color="7", desc="朝風呂派。15分でシャワー。"),
 dict(title="朝食", byday="MO,TU,WE,TH,FR", st="09:00", en="09:15", color="7", desc="食べながら Anki を10枚だけ。"),
 dict(title="身支度", byday="MO,TU,WE,TH,FR", st="09:15", en="09:30", color="7", desc="9:30 始業。"),
 dict(title="仕事", byday="MO,TU,WE,TH,FR", st="09:30", en="21:00", color="8", desc="祝日も勤務前提で入れてある。休みの日はこの枠を消して 14:00〜17:00 を科目B に使う。10/27(火) は 16:30 までに退社（17:15 金山で科目A-2）。"),
 dict(title="帰宅・夕食", byday="MO,TU,WE,TH,FR", st="21:00", en="22:00", color="7", desc="22:00 までに机に座る。"),
 dict(title="自由時間（勉強は休み）", byday="FR", st="22:00", en="23:30", color="2", desc="金曜夜は勉強なし。"),
 dict(title="就寝準備", byday="MO,TU,WE,TH,FR", st="23:30", en="24:00", color="7", desc="24:00 就寝 → 8:45 起床（約8.5時間）。"),
 # 土日（v3: 勉強は 14:00〜。家事は午前、筋トレは勉強のあと）
 dict(title="起床・風呂", byday="SA,SU", st="08:45", en="09:00", color="7", desc="朝風呂。"),
 dict(title="朝食", byday="SA,SU", st="09:00", en="09:30", color="7", desc="午前は家事と自由。勉強は 14:00 から。"),
 dict(title="家事（掃除・洗濯・買い出し）", byday="SA,SU", st="10:00", en="12:00", color="7", desc="v3(10/6): 午後 13:30 から午前へ移動。寝坊した日は短縮してよい（14:00 の勉強枠は守る）。"),
 dict(title="昼食", byday="SA,SU", st="12:30", en="13:30", color="7", desc="13:30〜14:00 で机に座る準備。"),
 dict(title="筋トレ", byday="SA,SU", st="17:30", en="18:30", color="6", desc="v3(10/6): 15:30 から勉強枠のあとへ移動。毎週土日1時間。"),
 dict(title="自由時間", byday="SA,SU", st="18:30", en="19:00", color="2", desc="勉強後の報酬。動画はここから（夕食後 20:00〜 も自由）。"),
 dict(title="夕食", byday="SA,SU", st="19:00", en="20:00", color="7", desc=""),
 dict(title="就寝準備", byday="SA,SU", st="23:30", en="24:00", color="7", desc="日曜 23:00 は燃えるゴミ（既存予定）。"),
]

# ============ 勉強：平日の固定枠（月・木、繰り返し） ============
# v3: 平日夜は1ユニット（22:00〜22:50、木の模試だけ 23:00）。タイトルの先頭は週次タスクの照合に使うので変えない。
STUDY_R = [
 dict(title="【SC】科目A-2 誤答演習＋Anki（1ユニット50分）", byday="MO", start="2026-09-07", until="2026-10-19", st="22:00", en="22:50", color="10",
      desc="v3(10/6〜): 1ユニット50分。過去問道場で科目A-2 の誤答から10〜15問（NW・サービスマネジメント・監査を優先）→ Anki 10分。06 音読は省略可。Focus To-Do で計測。終わったら動画は報酬。"),
 dict(title="【SC】科目A-2 25問模試（40分）＋答え合わせ（20分）", byday="TH", start="2026-09-10", until="2026-10-22", st="22:00", en="23:00", color="10",
      desc="v3(10/6〜): 過去問道場の模試モードで25問・40分（本番と同じ時間）→ 答え合わせ20分。誤答は月曜の誤答演習へ。目標 17/25。Anki は翌朝食時に。"),
 dict(title="【SC】科目B 仕組みドリル（Aリスト Anki・06 音読・P分類の見直し）", byday="MO", start="2026-11-02", until="2026-11-16", st="22:00", en="22:50", color="9",
      desc="1ユニット50分。§4.1 Aリスト18件の Anki → 06 の該当章を音読 → 日曜の通し演習の誤答 P 分類を見直す。新しい問は解かない（日曜の通し演習に温存）。"),
 dict(title="【SC】科目B 仕組みドリル（Aリスト Anki・06 音読・P分類の見直し）", byday="TH", start="2026-10-29", until="2026-11-19", st="22:00", en="22:50", color="9",
      desc="1ユニット50分。§4.1 Aリスト18件の Anki → 06 の該当章を音読 → 混同ペア（復号/復元、認証/認可 など）を口頭で説明。"),
]
ST_R = ("22:00", "22:50")   # 既定（各エントリの st/en が優先）

# ============ 勉強：個別（火・水・土・日） ============
# v2（〜10/7）: 火 22:00-23:30 = 科目B 解答 / 水 22:00-23:00 = 採点 / 土 9:30-12:30 / 日 9:30-12:00（週次レビューの overrides で置換済み）
# v3（10/10〜）: 土 14:00-16:30 = できれば枠 / 日 14:00-17:00 = 必須枠（通し演習の日は 13:30-17:30）/ 平日 22:00-22:50 = 1ユニット
S = []
def s(date, st, en, title, desc, color="9"):
    S.append(dict(date=date, start=st, end=en, title=title, desc=desc, color=color))
def pair(tue, wed, name, solve_desc, grade_desc):
    s(tue, "22:00", "23:30", "【SC】科目B %s 解答（65分・紙なし）" % name, solve_desc)
    s(wed, "22:00", "23:00", "【SC】科目B %s 採点・講評照合・P分類" % name, grade_desc)
def unit(date, title, desc, color="9", en="22:50"):
    s(date, "22:00", en, title, desc, color)
def sat(date, title, desc, color="9", st="14:00", en="16:30"):
    s(date, st, en, title, desc, color)
def sun(date, title, desc, color="9", st="14:00", en="17:00"):
    s(date, st, en, title, desc, color)

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
# W6 10/5-11（10/6・10/7 は overrides で1ユニットに置換済み。土日から v3） ------
pair("2026-10-06", "2026-10-07", "R6春 問3（XSS・CSRF・SSRF）",
     "紙解き済み → 採点アプリに入力し直す形で65分。Web は「1問だけ選ぶ前提で50%」が目標。",
     "採点・講評照合・P分類。SSRF の防御（許可リスト・メタデータ遮断）を説明できるか。")
sat("2026-10-10", "【SC】科目B R7春 問2（CVSS/EPSS/KEV・SBOM）解答＋採点",
    "10/3 予定分の回収。解答65分 → 採点アプリで採点・講評照合・P分類（45分）。柱②（脆弱性管理）。")
sun("2026-10-11", "【SC】科目B R5秋 問4（委託・リスク）解答＋採点",
    "10/4 予定分の回収。解答65分 → 採点アプリで採点・講評照合・P分類。柱②（委託・リスク）。\n▶ ゲート 10/11：採点済み累計13問・A-2 17/25（10/8 の模試）。")
# W7 10/12-18（A-2 2週前） --------------------------------------------
unit("2026-10-13", "【SC】科目A-2 過去問道場25問＋Anki（1ユニット50分）",
     "ネットワーク・サービスマネジメント・監査（TAC で落とした分野）を優先して解く。終わったら動画は報酬。", "10")
unit("2026-10-14", "【SC】科目B R6春 問3（XSS・CSRF・SSRF）紙解き答案を採点アプリに入力・採点（1ユニット50分）",
     "新たに解かない。紙の答案を採点アプリに入力して採点・講評照合・P分類まで。23:00 燃えるゴミの前に終える。")
sat("2026-10-17", "【SC】科目A-2 直近回模試（40分）＋誤答復習＋弱点分野 誤答演習",
    "過去問道場の模試モードで直近回25問・40分 → 答え合わせ20分 → NW・サービスマネジメント・監査の誤答を道場で20問 → Anki 化。\n▶ ゲート 10/18：10/15・10/17 の模試が2回とも 17/25 以上。", "10")
sun("2026-10-18", "【SC】科目B R7秋 問4（管理・委託）解答＋採点",
    "柱②。9/13 予定分の回収（未着手）。解答65分 → 採点アプリで採点・講評照合・P分類。")
# W8 10/19-25（A-2 直前週。10/19 月・10/22 木は A-2 固定枠の最終回） --------
unit("2026-10-20", "【SC】科目A-2 誤答つぶし＋Anki（1ユニット50分）",
     "10/15・10/17 の模試の誤答を道場で解き直し → Anki。SAML・TLS・問25枠（監査/内部統制）を重点。", "10")
unit("2026-10-21", "【SC】科目A-2 Anki 総ざらい（1ユニット50分）",
     "新しい問題は解かない。Anki の科目A-2 デッキ（4択デッキ含む）を回す。23:00 燃えるゴミの前に終える。", "10")
sat("2026-10-24", "【SC】科目A-2 模試×2（40分×2）＋答え合わせ",
    "受験3日前。直近回2セットを本番と同じ40分で。誤答は当日中に Anki 化。2回とも 17/25 以上なら 10/25 は予定どおり後半を科目B に。", "10")
sun("2026-10-25", "【SC】科目A-2 弱点分野 誤答演習（60分）→ 科目B R6秋 問3 解き直し（Web・アクセスログ）解答＋採点",
    "前半60分：10/24 の模試の誤答＋NW・監査を道場で。後半：R6秋 問3 解き直し（解答65分 → 採点45分、客観欄を落とさない）。9/19 ゲート未達の処置分。\n10/24 の模試が 17/25 未満なら後半も A-2 に全振り。")
unit("2026-10-26", "【SC】科目A-2 前日：Anki 総ざらい（新しい問題は解かない）",
     "明日 10/27（火）17:15 金山駅南口会場（第17フクマルビル2階）。本人確認書類（顔写真付き原本）・16:30 退社・経路を確認して早く寝る。", "5")
# 10/27（火）科目A-2 受験 17:15 金山（仕事は 16:30 までに切り上げ） -----------
unit("2026-10-27", "【SC】科目A-2 受験後：出題分野メモ＋休み",
     "受験直後に覚えている範囲で出題分野をメモ（CBT は問題非公開）。夜は休み。明日から科目B に全振り。", "11")
unit("2026-10-28", "【SC】科目B Aリスト Anki＋06 音読（1ユニット50分）",
     "受験翌日は軽め。§4.1 Aリスト18件の Anki → 06 の1章を音読。23:00 燃えるゴミの前に終える。")
# W9 10/26-11/1 -----------------------------------------------------
sat("2026-10-31", "【SC】科目B R7春 問1 解き直し（管理・委託）解答＋採点",
    "柱②の2回目。前回の P 分類メモを先に読んでから解答65分 → 採点・講評照合。前回比で伸びた欄／伸びない欄を記録。")
sun("2026-11-01", "【SC】通し演習① R6春（150分・紙なし）＋自己採点",
    "13:30〜16:00 本番形式：最初の10分で4問の設問だけ読み、枠判定・客観欄数・図表数をメモ機能に3行 → 2問選択（未演習の問2/問4を含める）→ 各65分 → 見直し10分。16:00〜17:30 採点アプリで2問を採点。講評照合・P分類は 11/2・11/3 の夜。\n▶ ゲート 11/1：2問で40点。", st="13:30", en="17:30")
# W10 11/2-8 --------------------------------------------------------
unit("2026-11-03", "【SC】通し①の講評照合・P分類（1ユニット50分）",
     "11/1 の2問を講評と照合し P0〜P12 に分類。時間配分（選択10分／各65分）の振り返りを3行メモ。")
unit("2026-11-04", "【SC】科目B Aリスト Anki＋06 音読（1ユニット50分）",
     "§4.1 Aリスト18件の Anki → 通し①で落とした仕組みの章を 06 で音読。23:00 燃えるゴミの前に終える。")
sat("2026-11-07", "【SC】科目B R5秋 問1 2回目（XSS）解答＋採点",
    "Web の2回目。前回 5% → 目標 50%。前回の P 分類メモを読んでから65分 → 採点・講評照合。客観欄を全部取る。")
sun("2026-11-08", "【SC】通し演習② R7秋（150分・紙なし）＋自己採点【前期判定】",
    "13:30〜16:00 本番形式（未演習の問3を含む4問から2問選択）→ 16:00〜17:30 採点。\n▶ 11/8 判定：初見2問・150分・紙なしで合計50点以上 → 前期で科目B合格圏。未満 → 受験はするが 11/9 以降は仕組みドリルと Web 解き直し中心、後期（2027/3/16〜28）を本命に。", st="13:30", en="17:30")
# W11 11/9-15 -------------------------------------------------------
unit("2026-11-10", "【SC】通し②の講評照合・P分類（1ユニット50分）",
     "11/8 の2問を講評と照合し P 分類。前期判定の結果に応じて 11/9 以降の重点を確認。")
unit("2026-11-11", "【SC】科目B Aリスト Anki＋06 音読（1ユニット50分）",
     "§4.1 Aリスト18件の Anki → 06 の該当章を音読。記述欄の字数（26〜45字）と句読点の癖を確認。23:00 燃えるゴミの前に終える。")
sat("2026-11-14", "【SC】科目B R6秋 問3 2回目（Web・アクセスログ）解答＋採点",
    "Web の2回目。客観欄（用語穴埋め・記号）を全部取るつもりで65分 → 採点・講評照合。1回目との差分を記録。")
sun("2026-11-15", "【SC】通し演習③ R5秋（150分・紙なし）＋自己採点",
    "13:30〜16:00 本番形式（未演習の問2/問3を含む4問から2問選択）→ 16:00〜17:30 採点。目標55点。", st="13:30", en="17:30")
# W12 11/16-22 ------------------------------------------------------
unit("2026-11-17", "【SC】通し③の講評照合・P分類＋06 音読（1ユニット50分）",
     "新しい問は解かない。11/15 の2問を講評と照合 → 06 を通しで音読（できる章まで）。")
unit("2026-11-18", "【SC】03 §4 チェックリスト＋時間配分の再確認（1ユニット50分）",
     "選択10分／各問65分／見直し10分。メモ機能に書く3行のフォーマットを決めておく。23:00 燃えるゴミの前に終える。")
sat("2026-11-21", "【SC】Aリスト18件 総点検＋混同ペア＋通し①〜③の P 分類メモ通読",
    "新しい問は解かない。§4.1 Aリスト18件を口頭で説明 → 混同ペア（復号/復元、認証/認可 など）→ 通し①〜③の P 分類メモを通読。")
sun("2026-11-22", "【SC】前日：03 §4 チェックリスト＋持ち物・会場確認",
    "新しい問題は解かない。本人確認書類（顔写真付き原本）・会場（CBT名駅桜通テストセンター、名駅3-22-8 大東海ビル2階。近隣会場と取り違えない）・15:30 開始・14:30 出発を確認して早く寝る。", "5", en="16:00")
# 11/23（月・祝）科目B 受験 15:30 名駅 ---------------------------------
s("2026-11-23", "10:00", "10:30", "【SC】当日：03 §4 チェックリストのみ → 14:30 出発",
  "新しい問題は解かない。チェックリストを読む → 昼食 → 14:30 出発（名駅、15:00 受付目安）。150分＝選択10分／各問65分／見直し10分。", "5")

# ============ 終日（ics/md 用） ============
A = [
 dict(start="2026-10-06", end="2026-10-06", title="【SC】申込開始（〜10/24 17:00）A-1免除申請・A/B同時予約"),
 dict(start="2026-10-17", end="2026-10-27", title="【SC】科目A 実施期間（10/17〜10/27）"),
 dict(start="2026-10-27", end="2026-10-27", title="【SC】科目A-2 受験（確定）17:15 金山駅南口会場"),
 dict(start="2026-11-11", end="2026-11-23", title="【SC】科目B 実施期間（11/11〜11/23）"),
 dict(start="2026-11-23", end="2026-11-23", title="【SC】科目B 受験（確定）15:30 CBT名駅桜通テストセンター"),
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
# v3 改訂（2026-10-06）は本体に直接反映した。履歴として1行だけ残す。
CHANGELOG.append(("2026-10-06", "改訂 v3", "2026-10-10〜11-23",
    "受験日確定（A-2 10/27(火)17:15 金山・科目B 11/23(月祝)15:30 名駅）に合わせて 10/10 以降を再編。土日の勉強を午後（土 14:00〜16:30＝できれば枠、日 14:00〜17:00＝必須枠）、平日夜を1ユニット50分（月・木の固定枠も 22:50／23:00 終了）に変更。通し演習①②③を日曜 11/1・11/8・11/15（13:30〜17:30、自己採点まで）に移動。10/24〜26 を A-2 直前に、10/27 夜を受験後の休みに。11/20 の前日枠を 11/22 に、11/23 当日チェックを追加。日課は家事を午前（10:00〜12:00）、筋トレを 17:30〜18:30 に移動。10/5 までの週次決定（10/10 R7春問2・10/11 R5秋問4・10/25 R6秋問3）は取り込み済み。未配置：R6秋 問4・R6秋 問2・R6秋 問1 解き直し・R7春 問3・R5秋 問4 2回目（祝日休みや余力があれば）。",
    "10/6 に申込・予約が確定し、受験日が予定より後ろ（10/24→10/27、11/21→11/23）になった。Focus To-Do 実績：土日 9:30 枠は8週連続ゼロ、平日夜は Anki 50分のみ成立、週 1.7〜6.0h。実際の開始時刻は 14〜17時と 20〜23時に集中。"))

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
def r_times(e):
    return e.get("st", ST_R[0]), e.get("en", ST_R[1])

# ---------------- ICS ----------------
lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//SC study v3//JP","CALSCALE:GREGORIAN","METHOD:PUBLISH",
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
    d0 = first_on(e["start"], e["byday"]); st, en = r_times(e)
    lines += vevent("r%02d" % i, ["DTSTART;TZID=%s:%s" % (TZ, ics_dt(d0, st)), "DTEND;TZID=%s:%s" % (TZ, ics_dt(d0, en)),
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
    st, en = r_times(e)
    while d <= until:
        if d.weekday() in days:
            weeks.setdefault(wk(d.isoformat()), []).append((d.isoformat(), st, en, e["title"], hours(st, en)))
        d += dt.timedelta(days=1)
JW = "月火水木金土日"
md = ["# 10_学習スケジュール_20260906", "",
 "> **作成日**：2026-09-06（v2 改訂 2026-09-07、**v3 改訂 2026-10-06：受験日確定に合わせて 10/10 以降を再編**。以降は毎週月曜 5:00 の週次レビューで更新。変更は §6）　**対象期間**：2026-09-07（月）〜 2026-11-23（月・祝、科目B 受験）",
 "> **受験日（確定、10/6 申込済）**：科目A-2 **2026-10-27（火）17:15** 金山駅南口会場（40分・25問。仕事は 16:30 までに切り上げる）／科目B **2026-11-23（月・祝）15:30** CBT名駅桜通テストセンター（150分。近隣会場と取り違えない）。科目A-1 は免除（2025年度 応用情報合格）。",
 "> **前提**：毎日 8:45 起床、風呂は朝。平日（祝日含む）は 9:30〜21:00 勤務（会社まで5分）。v3 は Focus To-Do の実績（土日 9:30 枠は8週連続ゼロ、平日夜は Anki 50分だけ成立、週 1.7〜6.0h、開始時刻は 14〜17時と 20〜23時）に合わせ、**土日の勉強を午後（14:00〜）、平日夜を1ユニット50分**にした。`09` §6 の必要時間 約61h のうち、残り7週で必須なのは通し演習3回と柱②・Web の解き直し。",
 "> **登録先**：Google カレンダー（petitgodzilla@gmail.com）。新Outlook に同アカウントが追加済みで、Outlook の予定表に同期表示されることを 9/7 に確認済み。outlook.jp 側に入れたい場合は `outputs/schedule/SC_study_schedule_2026.ics` を「予定表の追加 → ファイルからアップロード」で取り込む。", "",
 "## 1. 1日のテンプレート（v3）", "",
 "### 平日（月〜金、祝日も同じ）", "",
 "| 時刻 | 内容 |", "|---|---|",
 "| 8:45〜9:00 | 起床・風呂（朝） |", "| 9:00〜9:15 | 朝食（Anki 10枚） |", "| 9:15〜9:30 | 身支度 |",
 "| 9:30〜21:00 | 仕事（10/27 は 16:30 退社 → 17:15 金山で科目A-2） |", "| 21:00〜22:00 | 帰宅・夕食 |",
 "| 22:00〜22:50 | **勉強 1ユニット**（月：A-2 誤答＋Anki／火：A-2 道場25問＋Anki／水：科目B Aリスト Anki＋06 音読 or 紙解き分の入力採点／木：A-2 模試 〜23:00／金：休み）。10/28 以降は月・木が科目B 仕組みドリル、火が通し演習の講評照合 |",
 "| 22:50〜23:30 | 自由（動画は勉強後の報酬）。水曜 23:00 燃えるゴミ（既存） |", "| 23:30〜24:00 | 就寝準備（24:00 就寝、8:45 起床） |", "",
 "### 土日", "",
 "| 時刻 | 内容 |", "|---|---|",
 "| 8:45〜9:00 | 起床・風呂（朝） |", "| 9:00〜9:30 | 朝食 |",
 "| 9:30〜10:00 | 自由（寝坊してもここまで） |",
 "| 10:00〜12:00 | 家事（掃除・洗濯・買い出し）※v3 で午後から移動 |",
 "| 12:30〜13:30 | 昼食（13:30〜14:00 で机に座る） |",
 "| 14:00〜17:00 | **勉強**（土は〜16:30＝できれば枠／日は必須枠：科目B 1問 解答＋採点。通し演習の日は 13:30〜17:30） |",
 "| 17:30〜18:30 | 筋トレ ※v3 で勉強後に移動 |", "| 18:30〜19:00 | 自由（勉強後の報酬） |",
 "| 19:00〜20:00 | 夕食 |", "| 20:00〜23:30 | 自由。日曜 23:00 燃えるゴミ（既存） |", "| 23:30〜24:00 | 就寝準備 |", "",
 "勉強時間は **平日 月〜木 50分×4（木は60分）＋土 2.5h＋日 3h（通し演習の日は 4h）＝ 週約 9h**。直近6週の実績は平均 4h なので、**日曜午後を必須、土曜と平日は上積み**として扱う（やらなかった平日は取り返さない）。10/27 の科目A-2 受験後は平日夜も科目B に切り替わる。", "",
 "## 2. 週次カレンダー（勉強のみ）", ""]
total = 0
for w in sorted(weeks):
    items = sorted(weeks[w]); h = sum(x[4] for x in items); total += h
    md += ["### %s〜%s　計 %.1fh" % (w.strftime("%m/%d"), (w + dt.timedelta(days=6)).strftime("%m/%d"), h), "", "| 日 | 時刻 | 内容 |", "|---|---|---|"]
    for d, st, en, t, hh in items:
        dd = dt.date.fromisoformat(d)
        md.append("| %s(%s) | %s〜%s | %s |" % (dd.strftime("%m/%d"), JW[dd.weekday()], st, en, t.replace("【SC】", "")))
    md.append("")
md += ["**合計 約%.0fh**（`09` §6.2 の必要量 約61h に対し余裕 約%.0fh。ただし実績ベースでは日曜枠だけで約 20h）" % (total, total - 61), "",
 "## 3. 節目（終日イベント）", "", "| 日付 | 内容 |", "|---|---|"]
for e in A:
    md.append("| %s%s | %s |" % (e["start"], "" if e["start"] == e["end"] else "〜" + e["end"], e["title"].replace("【SC】", "")))
md.append("| 2026-10-06 12:00 | 試験申込・会場予約（済。A-1 免除申請、A-2 10/27 17:15 金山・科目B 11/23 15:30 名駅を予約） |")
GATES = [
 ("2026-09-13", "採点済み累計10問", "9/27 の予備枠で回収"),
 ("2026-09-19", "Web 2問（R5秋問1・R6秋問3）とも 20% 以上", "10/25 の予備枠を Web に振り替え"),
 ("2026-09-27", "採点済み累計13問", "10/4 の仕組みドリルを科目B に寄せる"),
 ("2026-10-11", "A-2 17/25（10/8 模試）、採点済み累計13問", "10/17・10/18 を A-2 に全振り"),
 ("2026-10-18", "A-2 模試 2回連続 17/25 以上（10/15・10/17）", "10/24・10/25 を両方 A-2 に全振り（科目B は 10/28 以降）"),
 ("2026-11-01", "通し① 2問で 40点", "—"),
 ("2026-11-08", "通し② 2問で 50点 → 前期本番", "受験はする。11/9 以降は仕組みドリル＋Web 解き直し中心、後期（2027/3/16〜28）本命に切替"),
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
 "- 優先順位：**日曜午後＝必須**（科目B 1問 or 通し演習）＞ 土曜午後＝できれば ＞ 平日夜＝1ユニット（できた日だけ）。やらなかった平日は取り返さない。土曜が飛んだら日曜の内容を優先し、土曜分は落とす。",
 "- 動画は「1ユニット（25〜50分）を終えた後の報酬」。勉強の前に開かない。",
 "- 10/27（火）は 16:30 までに退社して金山駅南口会場へ（受付 17:00 目安、顔写真付き本人確認書類の原本）。11/23（月・祝）は仕事を入れず 14:30 に出発（CBT名駅桜通テストセンター、15:30 開始）。",
 "- 祝日（10/12・11/3）が休みなら 14:00〜17:00 を科目B 1問（未配置：R6秋 問4、R6秋 問2、R6秋 問1 解き直し）に充てる。",
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
    period=dict(start=START, end=PERIOD_END),
    template=dict(weekday="月〜木 22:00〜22:50 の1ユニット（木は〜23:00）", weekend="土 14:00〜16:30／日 14:00〜17:00（通し演習の日は 13:30〜17:30）", weeklyHours=9),
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
