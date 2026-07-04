# 情報処理安全確保支援士 過去問 一括ダウンロード
# 出力先フォルダ
$baseDir = "C:\SC\IPA_SC_Mondai"
$baseUrl = "https://www.ipa.go.jp"

# [フォルダ名, ファイル名, ディレクトリID]
$files = @(
    # ---- 2017 平成29年度 ----
    # 春期
    @("2017_H29\春期", "2017h29h_koudo_am1_qs.pdf",    "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_koudo_am1_ans.pdf",   "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_am2_qs.pdf",       "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_am2_ans.pdf",      "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_pm1_qs.pdf",       "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_pm1_ans.pdf",      "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_pm1_cmnt.pdf",     "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_pm2_qs.pdf",       "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_pm2_ans.pdf",      "gmcbt8000000fzx1-att"),
    @("2017_H29\春期", "2017h29h_sc_pm2_cmnt.pdf",     "gmcbt8000000fzx1-att"),
    # 秋期
    @("2017_H29\秋期", "2017h29a_koudo_am1_qs.pdf",    "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_koudo_am1_ans.pdf",   "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_am2_qs.pdf",       "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_am2_ans.pdf",      "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_pm1_qs.pdf",       "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_pm1_ans.pdf",      "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_pm1_cmnt.pdf",     "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_pm2_qs.pdf",       "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_pm2_ans.pdf",      "gmcbt8000000fqpm-att"),
    @("2017_H29\秋期", "2017h29a_sc_pm2_cmnt.pdf",     "gmcbt8000000fqpm-att"),

    # ---- 2018 平成30年度 ----
    # 春期
    @("2018_H30\春期", "2018h30h_koudo_am1_qs.pdf",    "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_koudo_am1_ans.pdf",   "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_am2_qs.pdf",       "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_am2_ans.pdf",      "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_pm1_qs.pdf",       "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_pm1_ans.pdf",      "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_pm1_cmnt.pdf",     "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_pm2_qs.pdf",       "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_pm2_ans.pdf",      "gmcbt8000000fabr-att"),
    @("2018_H30\春期", "2018h30h_sc_pm2_cmnt.pdf",     "gmcbt8000000fabr-att"),
    # 秋期
    @("2018_H30\秋期", "2018h30a_koudo_am1_qs.pdf",    "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_koudo_am1_ans.pdf",   "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_am2_qs.pdf",       "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_am2_ans.pdf",      "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_pm1_qs.pdf",       "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_pm1_ans.pdf",      "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_pm1_cmnt.pdf",     "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_pm2_qs.pdf",       "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_pm2_ans.pdf",      "gmcbt8000000f01f-att"),
    @("2018_H30\秋期", "2018h30a_sc_pm2_cmnt.pdf",     "gmcbt8000000f01f-att"),

    # ---- 2019 平成31/令和元年度 ----
    # 春期 (H31)
    @("2019_H31\春期", "2019h31h_koudo_am1_qs.pdf",    "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_koudo_am1_ans.pdf",   "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_am2_qs.pdf",       "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_am2_ans.pdf",      "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_pm1_qs.pdf",       "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_pm1_ans.pdf",      "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_pm1_cmnt.pdf",     "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_pm2_qs.pdf",       "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_pm2_ans.pdf",      "gmcbt8000000ddiw-att"),
    @("2019_H31\春期", "2019h31h_sc_pm2_cmnt.pdf",     "gmcbt8000000ddiw-att"),
    # 秋期 (R01)
    @("2019_H31\秋期", "2019r01a_koudo_am1_qs.pdf",    "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_koudo_am1_ans.pdf",   "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_am2_qs.pdf",       "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_am2_ans.pdf",      "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_pm1_qs.pdf",       "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_pm1_ans.pdf",      "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_pm1_cmnt.pdf",     "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_pm2_qs.pdf",       "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_pm2_ans.pdf",      "gmcbt8000000dict-att"),
    @("2019_H31\秋期", "2019r01a_sc_pm2_cmnt.pdf",     "gmcbt8000000dict-att"),

    # ---- 2020 令和2年度 (春期中止・秋期のみ) ----
    @("2020_R02\秋期", "2020r02o_koudo_am1_qs.pdf",    "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_koudo_am1_ans.pdf",   "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_am2_qs.pdf",       "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_am2_ans.pdf",      "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_pm1_qs.pdf",       "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_pm1_ans.pdf",      "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_pm1_cmnt.pdf",     "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_pm2_qs.pdf",       "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_pm2_ans.pdf",      "gmcbt8000000d05l-att"),
    @("2020_R02\秋期", "2020r02o_sc_pm2_cmnt.pdf",     "gmcbt8000000d05l-att"),

    # ---- 2021 令和3年度 ----
    # 春期
    @("2021_R03\春期", "2021r03h_koudo_am1_qs.pdf",    "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_koudo_am1_ans.pdf",   "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_am2_qs.pdf",       "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_am2_ans.pdf",      "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_pm1_qs.pdf",       "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_pm1_ans.pdf",      "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_pm1_cmnt.pdf",     "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_pm2_qs.pdf",       "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_pm2_ans.pdf",      "gmcbt8000000d5ru-att"),
    @("2021_R03\春期", "2021r03h_sc_pm2_cmnt.pdf",     "gmcbt8000000d5ru-att"),
    # 秋期
    @("2021_R03\秋期", "2021r03a_koudo_am1_qs.pdf",    "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_koudo_am1_ans.pdf",   "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_am2_qs.pdf",       "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_am2_ans.pdf",      "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_pm1_qs.pdf",       "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_pm1_ans.pdf",      "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_pm1_cmnt.pdf",     "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_pm2_qs.pdf",       "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_pm2_ans.pdf",      "gmcbt8000000apad-att"),
    @("2021_R03\秋期", "2021r03a_sc_pm2_cmnt.pdf",     "gmcbt8000000apad-att"),

    # ---- 2022 令和4年度 ----
    # 春期
    @("2022_R04\春期", "2022r04h_koudo_am1_qs.pdf",    "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_koudo_am1_ans.pdf",   "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_am2_qs.pdf",       "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_am2_ans.pdf",      "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_pm1_qs.pdf",       "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_pm1_ans.pdf",      "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_pm1_cmnt.pdf",     "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_pm2_qs.pdf",       "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_pm2_ans.pdf",      "gmcbt80000009sgk-att"),
    @("2022_R04\春期", "2022r04h_sc_pm2_cmnt.pdf",     "gmcbt80000009sgk-att"),
    # 秋期
    @("2022_R04\秋期", "2022r04a_koudo_am1_qs.pdf",    "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_koudo_am1_ans.pdf",   "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_am2_qs.pdf",       "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_am2_ans.pdf",      "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_pm1_qs.pdf",       "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_pm1_ans.pdf",      "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_pm1_cmnt.pdf",     "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_pm2_qs.pdf",       "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_pm2_ans.pdf",      "gmcbt80000008smf-att"),
    @("2022_R04\秋期", "2022r04a_sc_pm2_cmnt.pdf",     "gmcbt80000008smf-att"),

    # ---- 2023 令和5年度 ----
    # 春期 (午後Ⅰ・Ⅱ分離)
    @("2023_R05\春期", "2023r05h_koudo_am1_qs.pdf",    "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_koudo_am1_ans.pdf",   "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_am2_qs.pdf",       "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_am2_ans.pdf",      "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_pm1_qs.pdf",       "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_pm1_ans.pdf",      "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_pm1_cmnt.pdf",     "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_pm2_qs.pdf",       "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_pm2_ans.pdf",      "ps6vr70000010d6y-att"),
    @("2023_R05\春期", "2023r05h_sc_pm2_cmnt.pdf",     "ps6vr70000010d6y-att"),
    # 秋期 (午後統合)
    @("2023_R05\秋期", "2023r05a_koudo_am1_qs.pdf",    "ps6vr70000010d6y-att"),
    @("2023_R05\秋期", "2023r05a_koudo_am1_ans.pdf",   "ps6vr70000010d6y-att"),
    @("2023_R05\秋期", "2023r05a_sc_am2_qs.pdf",       "ps6vr70000010d6y-att"),
    @("2023_R05\秋期", "2023r05a_sc_am2_ans.pdf",      "ps6vr70000010d6y-att"),
    @("2023_R05\秋期", "2023r05a_sc_pm_qs.pdf",        "ps6vr70000010d6y-att"),
    @("2023_R05\秋期", "2023r05a_sc_pm_ans.pdf",       "ps6vr70000010d6y-att"),
    @("2023_R05\秋期", "2023r05a_sc_pm_cmnt.pdf",      "ps6vr70000010d6y-att"),

    # ---- 2024 令和6年度 ----
    # 春期
    @("2024_R06\春期", "2024r06h_koudo_am1_qs.pdf",    "m42obm000000afqx-att"),
    @("2024_R06\春期", "2024r06h_koudo_am1_ans.pdf",   "m42obm000000afqx-att"),
    @("2024_R06\春期", "2024r06h_sc_am2_qs.pdf",       "m42obm000000afqx-att"),
    @("2024_R06\春期", "2024r06h_sc_am2_ans.pdf",      "m42obm000000afqx-att"),
    @("2024_R06\春期", "2024r06h_sc_pm_qs.pdf",        "m42obm000000afqx-att"),
    @("2024_R06\春期", "2024r06h_sc_pm_ans.pdf",       "m42obm000000afqx-att"),
    @("2024_R06\春期", "2024r06h_sc_pm_cmnt.pdf",      "m42obm000000afqx-att"),
    # 秋期
    @("2024_R06\秋期", "2024r06a_koudo_am1_qs.pdf",    "m42obm000000afqx-att"),
    @("2024_R06\秋期", "2024r06a_koudo_am1_ans.pdf",   "m42obm000000afqx-att"),
    @("2024_R06\秋期", "2024r06a_sc_am2_qs.pdf",       "m42obm000000afqx-att"),
    @("2024_R06\秋期", "2024r06a_sc_am2_ans.pdf",      "m42obm000000afqx-att"),
    @("2024_R06\秋期", "2024r06a_sc_pm_qs.pdf",        "m42obm000000afqx-att"),
    @("2024_R06\秋期", "2024r06a_sc_pm_ans.pdf",       "m42obm000000afqx-att"),
    @("2024_R06\秋期", "2024r06a_sc_pm_cmnt.pdf",      "m42obm000000afqx-att"),

    # ---- 2025 令和7年度 ----
    # 春期
    @("2025_R07\春期", "2025r07h_koudo_am1_qs.pdf",    "nl10bi0000009lh8-att"),
    @("2025_R07\春期", "2025r07h_koudo_am1_ans.pdf",   "nl10bi0000009lh8-att"),
    @("2025_R07\春期", "2025r07h_sc_am2_qs.pdf",       "nl10bi0000009lh8-att"),
    @("2025_R07\春期", "2025r07h_sc_am2_ans.pdf",      "nl10bi0000009lh8-att"),
    @("2025_R07\春期", "2025r07h_sc_pm_qs.pdf",        "nl10bi0000009lh8-att"),
    @("2025_R07\春期", "2025r07h_sc_pm_ans.pdf",       "nl10bi0000009lh8-att"),
    @("2025_R07\春期", "2025r07h_sc_pm_cmnt.pdf",      "nl10bi0000009lh8-att"),
    # 秋期
    @("2025_R07\秋期", "2025r07a_koudo_am1_qs.pdf",    "nl10bi0000009lh8-att"),
    @("2025_R07\秋期", "2025r07a_koudo_am1_ans.pdf",   "nl10bi0000009lh8-att"),
    @("2025_R07\秋期", "2025r07a_sc_am2_qs.pdf",       "nl10bi0000009lh8-att"),
    @("2025_R07\秋期", "2025r07a_sc_am2_ans.pdf",      "nl10bi0000009lh8-att"),
    @("2025_R07\秋期", "2025r07a_sc_pm_qs.pdf",        "nl10bi0000009lh8-att"),
    @("2025_R07\秋期", "2025r07a_sc_pm_ans.pdf",       "nl10bi0000009lh8-att"),
    @("2025_R07\秋期", "2025r07a_sc_pm_cmnt.pdf",      "nl10bi0000009lh8-att")
)

$success = 0
$skip    = 0
$fail    = 0
$total   = $files.Count

Write-Host "ダウンロード開始: 全 $total ファイル" -ForegroundColor Cyan

foreach ($entry in $files) {
    $subDir   = $entry[0]
    $fileName = $entry[1]
    $dirId    = $entry[2]

    $destDir  = Join-Path $baseDir $subDir
    $destFile = Join-Path $destDir $fileName
    $url      = "$baseUrl/shiken/mondai-kaiotu/$dirId/$fileName"

    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Force $destDir | Out-Null
    }

    if (Test-Path $destFile) {
        Write-Host "  SKIP: $fileName" -ForegroundColor Gray
        $skip++
        continue
    }

    try {
        Invoke-WebRequest -Uri $url -OutFile $destFile -UseBasicParsing -TimeoutSec 30
        Write-Host "  OK:   $subDir\$fileName" -ForegroundColor Green
        $success++
    } catch {
        Write-Host "  FAIL: $subDir\$fileName  [$($_.Exception.Message)]" -ForegroundColor Red
        $fail++
        if (Test-Path $destFile) { Remove-Item $destFile -Force }
    }

    Start-Sleep -Milliseconds 300
}

Write-Host ""
Write-Host "==== 完了 ====" -ForegroundColor Cyan
Write-Host "成功: $success  スキップ: $skip  失敗: $fail" -ForegroundColor Yellow
Write-Host "保存先: $baseDir"
