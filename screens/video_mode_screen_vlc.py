import tkinter as tk
import utils.settings_manager as settings_manager
import os
import random
from datetime import datetime
import threading
from time import strftime, localtime, time
import vlc
from tkinter import messagebox
import screens.video_mode_setting_screen as video_mode_setting_screen

# フォントサイズ設定
DATE_FONT_SIZE = 28
TIME_FONT_SIZE = 70
TEXT_COLOR = "white"

class VideoModeScreenVLC:
    def __init__(self):
        self.image_brightness = 1.0
        self.volume = 1.0
        self.current_video_index = 0
        self.last_video_change_time = time()

        self.initialize_settings()
        self.create_widgets()

    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.video_path = settings.get('video_path')
        self.interval = int(settings.get('interval'))
        self.play_video_audio = settings.get('play_video_audio', True)

        self.video_files = [f for f in os.listdir(self.video_path) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    def create_widgets(self):
        self.root = tk.Tk()
        self.root.title("Video Display App (VLC)")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.date_label = tk.Label(self.root, text="", fg=TEXT_COLOR, bg="black",
                                   font=("calibri", DATE_FONT_SIZE, "bold"))
        self.date_label.place(relx=0.5, rely=0.85, anchor="center")

        self.time_label = tk.Label(self.root, text="", fg=TEXT_COLOR, bg="black",
                                   font=("calibri", TIME_FONT_SIZE, "bold"))
        self.time_label.place(relx=0.5, rely=0.92, anchor="center")

        self.instance = vlc.Instance(['--no-xlib', '--quiet', '--no-video-title-show'])
        self.player = self.instance.media_player_new()

        self.play_random_video()
        self.update_time_labels()

        self.root.bind('<Escape>', lambda e: self.close_window())
        self.root.bind('<space>', lambda e: self.next_video())

        self.root.mainloop()

    def play_random_video(self):
        if not self.video_files:
            print("動画ファイルが見つかりません")
            return

        random_file = random.choice(self.video_files)
        video_path = os.path.join(self.video_path, random_file)
        self.current_video_path = video_path

        media = self.instance.media_new(video_path, 'input-repeat=999')
        self.player.set_media(media)

        if not self.play_video_audio:
            self.player.audio_set_volume(0)

        self.player.play()

        self.root.update_idletasks()
        if os.name == 'nt':
            self.player.set_hwnd(self.root.winfo_id())
        else:
            self.player.set_xwindow(self.root.winfo_id())

        print(f"動画再生開始: {random_file}")

    def next_video(self):
        self.play_random_video()

    def update_time_labels(self):
        current_date = strftime('%Y-%m-%d %A', localtime())
        current_time = strftime('%H:%M:%S')
        self.date_label.config(text=current_date)
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time_labels)

    def close_window(self):
        print("終了します")
        self.player.stop()
        self.root.destroy()
        video_mode_setting_screen.create_screen()

def create_screen():
    try:
        VideoModeScreenVLC()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        messagebox.showerror("Error", f"動画再生エラー: {e}")
        video_mode_setting_screen.create_screen()
