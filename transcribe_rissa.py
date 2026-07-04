import subprocess
import os
import sys

YTDLP   = r"C:\Users\petit\AppData\Roaming\Python\Python313\Scripts\yt-dlp.exe"
WHISPER = r"C:\Users\petit\AppData\Roaming\Python\Python313\Scripts\whisper.exe"
FFMPEG_DIR = r"C:\Users\petit\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"

OUT_DIR   = r"C:\SC\rissa_transcripts"
AUDIO_DIR = os.path.join(OUT_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

env = os.environ.copy()
env["PATH"] = FFMPEG_DIR + ";" + env.get("PATH", "")

VIDEOS = [
    ("_HdCNxvmkkE", "13_R7秋_解答解説"),
    ("wvBzOohQzjI",  "12_R7春_解答解説"),
    ("DOZ6_7P1AEI",  "11_AIにR7春解かせよう"),
    ("4WHo0507naw",  "10_R6秋_解答解説"),
    ("-2ICxQFYIes",  "09_R6春_解答解説"),
    ("9l5BcHKHjL4",  "08_R5秋_解答解説"),
    ("FfwYokKF-S8",  "07_R5春_解答解説"),
    ("rLPHyfkmBHM",  "06_R4秋_解答解説"),
    ("sfXVeojrwrY",  "05_R4春_解答解説"),
    ("WootX6IFd0g",  "04_R3秋_解答解説"),
    ("GeyT_4zx1cE",  "03_R3春_解答解説"),
    ("NYZVPDysN_4",  "02_R2春_午後_出題予想"),
    ("kEoWYbB-r7U",  "01_R2春_午前_出題予想"),
]

for i, (vid_id, name) in enumerate(VIDEOS, 1):
    print(f"\n=== [{i}/{len(VIDEOS)}] {name} ===", flush=True)
    url        = f"https://www.youtube.com/watch?v={vid_id}"
    audio_path = os.path.join(AUDIO_DIR, f"{name}.mp3")
    txt_path   = os.path.join(OUT_DIR, f"{name}.txt")

    # 1. 音声ダウンロード
    if os.path.exists(audio_path):
        print("  音声ファイル既存 → スキップ", flush=True)
    else:
        print("  [1/2] 音声ダウンロード中...", flush=True)
        result = subprocess.run([
            YTDLP,
            "--no-check-certificate",
            "-x", "--audio-format", "mp3",
            "--ffmpeg-location", FFMPEG_DIR,
            "-o", os.path.join(AUDIO_DIR, f"{name}.%(ext)s"),
            url
        ], capture_output=False, env=env)
        if not os.path.exists(audio_path):
            print(f"  ダウンロード失敗 → スキップ", flush=True)
            continue

    # 2. Whisper文字起こし
    if os.path.exists(txt_path):
        print("  文字起こし済み → スキップ", flush=True)
    else:
        print("  [2/2] Whisper文字起こし中（smallモデル/日本語）...", flush=True)
        subprocess.run([
            WHISPER, audio_path,
            "--model", "small",
            "--language", "Japanese",
            "--output_dir", OUT_DIR,
            "--output_format", "txt"
        ], env=env)
        print(f"  完了: {txt_path}", flush=True)

print("\n=== 全処理完了 ===", flush=True)
print(f"結果フォルダ: {OUT_DIR}", flush=True)
