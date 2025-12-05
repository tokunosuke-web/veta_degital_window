# screens/youtube_mode_screen.py
import subprocess

YOUTUBE_VIDEO_ID = "v0ZQU2gq_J0"

def start_youtube_stream():
    # 埋め込み用URL（自動再生・ループ・コントロール非表示）
    url = (
        f"https://www.youtube.com/embed/{YOUTUBE_VIDEO_ID}"
        f"?autoplay=1&controls=0&loop=1&playlist={YOUTUBE_VIDEO_ID}&mute=0"
    )

    # Chromium をキオスクモード（全画面）で起動
    subprocess.Popen([
        "chromium-browser",
        "--kiosk",
        "--noerrdialogs",
        "--disable-infobars",
        "--incognito",
        url
    ])
