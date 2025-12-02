import tkinter as tk
import screens.video_mode_setting_screen as video_mode_setting_screen
import utils.settings_manager as settings_manager
import random
import threading
from tkinter import messagebox
from time import time, strftime, localtime
import mpv

class VideoModeScreenPygame:
    def __init__(self):
        self.current_video_index = 0
        self.last_video_change_time = time()
        self.running = True
        self.initialize_settings()
        self.play_next_youtube_video()

    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.interval = int(settings.get('interval'))
        self.show_time = True

        # ✅ YouTubeのURLだけを動画リストに追加
        self.video_files = [
            "https://youtu.be/K8vjx3FjhwI?si=6IIxucVD7YanOr-f"
        ]

    def play_next_youtube_video(self):
        # ランダム選択
        url = random.choice(self.video_files)
        print(f"再生開始: {url}")
        try:
            player = mpv.MPV(fullscreen=True, loop="inf")
            player.play(url)
            player.wait_for_playback()
        except Exception as e:
            print(f"再生エラー: {e}")
            messagebox.showerror("再生エラー", str(e))
            self.close_window()

    def close_window(self):
        print("終了します")
        self.running = False
        video_mode_setting_screen.create_screen()

def create_screen():
    try:
        VideoModeScreenPygame()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        messagebox.showerror("Error", f"動画再生エラー: {e}")
        video_mode_setting_screen.create_screen()
