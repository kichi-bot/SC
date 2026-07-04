import subprocess
import os

WHISPER = r"C:\Users\petit\AppData\Roaming\Python\Python313\Scripts\whisper.exe"
FFMPEG_DIR = r"C:\Users\petit\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
AUDIO_DIR = r"C:\SC\rissa_transcripts\audio"
OUT_DIR   = r"C:\SC\rissa_transcripts"

env = os.environ.copy()
env["PATH"] = FFMPEG_DIR + ";" + env.get("PATH", "")

mp3_files = sorted([f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")])
total = len(mp3_files)

for i, fname in enumerate(mp3_files, 1):
    name = os.path.splitext(fname)[0]
    audio_path = os.path.join(AUDIO_DIR, fname)
    txt_path   = os.path.join(OUT_DIR, f"{name}.txt")

    print(f"\n=== [{i}/{total}] {name} ===", flush=True)

    if os.path.exists(txt_path) and os.path.getsize(txt_path) > 100:
        print("  既存ファイルあり → スキップ", flush=True)
        continue

    print("  文字起こし中（small/日本語）...", flush=True)
    subprocess.run([
        WHISPER, audio_path,
        "--model", "small",
        "--language", "Japanese",
        "--output_dir", OUT_DIR,
        "--output_format", "txt"
    ], env=env)
    print(f"  完了: {txt_path}", flush=True)

print("\n=== 全処理完了 ===", flush=True)
