# SC午前Ⅱ 分析結果レビュー用チェックリスト

作成日:2026-07-06 / 指示書:`prompts/claude_sc_am2_trend_analysis.md`

## 対象範囲

- [x] 午前Ⅱだけを対象にしている(`sc_kakomon.json` の `section=午前Ⅱ` 825問のみ集計)
- [x] 午前Ⅰを混ぜていない(`section=午前Ⅰ` 990問は除外)
- [x] `koudo_am1` を混ぜていない(`*_koudo_am1_*.pdf` 全34ファイルを除外として記録)
- [x] 午後問題を集計対象にしていない(午後との関連は`pm_relevance`列・「午後とのつながり」欄での言及のみ)

## 成果物

- [x] `docs/sc_am2_trend.md` がある
- [x] `docs/sc_am2_strategy.md` がある
- [x] `data/sc_am2_questions.csv` がある(825行+ヘッダー、指定13列)
- [x] `data/sc_am2_topic_summary.csv` がある(14カテゴリ、指定6列)
- [x] `docs/sc_am2_flashcards.md` がある
- [x] `docs/sc_am2_30min_plan.md` がある
- [x] `docs/sc_am2_terms_diff.md` がある

## 内容

- [x] 頻出分野が明確(カテゴリ別出題数+直近重み付きスコア。trend.md冒頭に結論)
- [x] 優先順位が明確(A〜Dの4段階。trend.md末尾の一覧+CSVのpriority列)
- [x] 1日30分で実行できる(30min_plan.mdは1日単位のタスクに分解済み)
- [x] 暗記と仕組み理解を分けている(CSVのlearning_type列=memory/mechanism/both、strategy.mdで区別)
- [x] 午後につながる分野が明記されている(各カテゴリの「午後とのつながり」+pm_relevance列)
- [x] 似た用語の違いが整理されている(terms_diff.mdに12組+新用語対比)
- [x] スマホで読みやすいMarkdownになっている(横長表は最小限、見出し+短い箇条書き中心。詳細データはCSVに分離)

## 既知の制約(正直な注記)

- カテゴリ分類はキーワードベースの自動分類(825問中「その他」6問まで解消)。境界例で数%の誤差があり得る
- `season`列は spring/autumn の2値制約のため、平成23年**特別**(春期代替)は spring として記録
- 問題文の出典は sc-siken.com のスクレイプデータ。IPA原本PDF(2017年以降)はファイル名参照のみで本文照合はしていない
- `trap_point`はカテゴリ単位の典型ひっかけを設定(問題個別の分析は鉄板問題のみ trend.md/flashcards.md に記載)
