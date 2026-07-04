# JP-RISSA セミナー動画 文字起こしスクリプト
$ytdlp   = "C:\Users\petit\AppData\Roaming\Python\Python313\Scripts\yt-dlp.exe"
$whisper = "C:\Users\petit\AppData\Roaming\Python\Python313\Scripts\whisper.exe"
$ffmpegDir = "C:\Users\petit\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
$env:PATH = "$ffmpegDir;$env:PATH"

$outDir = "C:\SC\rissa_transcripts"
$audioDir = "$outDir\audio"
New-Item -ItemType Directory -Force $outDir | Out-Null
New-Item -ItemType Directory -Force $audioDir | Out-Null

$videos = @(
    @{ id = "_HdCNxvmkkE"; name = "13_R7秋_解答解説" },
    @{ id = "wvBzOohQzjI";  name = "12_R7春_解答解説" },
    @{ id = "DOZ6_7P1AEI";  name = "11_AIにR7春解かせよう" },
    @{ id = "4WHo0507naw";  name = "10_R6秋_解答解説" },
    @{ id = "-2ICxQFYIes";  name = "09_R6春_解答解説" },
    @{ id = "9l5BcHKHjL4";  name = "08_R5秋_解答解説" },
    @{ id = "FfwYokKF-S8";  name = "07_R5春_解答解説" },
    @{ id = "rLPHyfkmBHM";  name = "06_R4秋_解答解説" },
    @{ id = "sfXVeojrwrY";  name = "05_R4春_解答解説" },
    @{ id = "WootX6IFd0g";  name = "04_R3秋_解答解説" },
    @{ id = "GeyT_4zx1cE";  name = "03_R3春_解答解説" },
    @{ id = "NYZVPDysN_4";  name = "02_R2春_午後_出題予想" },
    @{ id = "kEoWYbB-r7U";  name = "01_R2春_午前_出題予想" }
)

$total = $videos.Count
$i = 0

foreach ($v in $videos) {
    $i++
    $url = "https://www.youtube.com/watch?v=$($v.id)"
    $audioPath = "$audioDir\$($v.name).mp3"
    $txtPath   = "$outDir\$($v.name).txt"

    Write-Host "=== [$i/$total] $($v.name) ===" -ForegroundColor Cyan

    # 1. 音声ダウンロード（スキップ可）
    if (Test-Path $audioPath) {
        Write-Host "  音声ファイル既存 → スキップ"
    } else {
        Write-Host "  [1/2] 音声ダウンロード中..."
        & $ytdlp --no-check-certificate -x --audio-format mp3 --ffmpeg-location $ffmpegDir `
            -o "$audioDir\$($v.name).%(ext)s" $url 2>&1 | Where-Object { $_ -notmatch "^WARNING" }
        if (-not (Test-Path $audioPath)) {
            Write-Host "  ダウンロード失敗 → スキップ" -ForegroundColor Red
            continue
        }
    }

    # 2. Whisper文字起こし（スキップ可）
    if (Test-Path $txtPath) {
        Write-Host "  文字起こし済み → スキップ"
    } else {
        Write-Host "  [2/2] Whisper文字起こし中（smallモデル/日本語）..."
        & $whisper $audioPath --model small --language Japanese --output_dir $outDir `
            --output_format txt 2>&1 | Where-Object { $_ -notmatch "^100%" }
        Write-Host "  完了: $txtPath" -ForegroundColor Green
    }
}

Write-Host "`n=== 全処理完了 ===" -ForegroundColor Green
Write-Host "結果フォルダ: $outDir"
