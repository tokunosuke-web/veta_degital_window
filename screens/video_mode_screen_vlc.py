from tkinter import Tk, Label
from datetime import datetime
import tkinter as tk
import vlc
import os

def video_mode_screen(video_folder):
    root = Tk()
    root.attributes("-fullscreen", True)

    # 日付と時刻表示ラベル（背景なしで前面に表示）
    label_time = Label(root, fg="white", bg="", font=("Helvetica", 36))
    label_time.place(relx=0.5, rely=0.9, anchor="center")
    label_time.lift()  # 常に前面に

    def update_time():
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        label_time.config(text=now)
        label_time.lift()  # 定期的に前面へ（念のため）
        root.after(1000, update_time)

    update_time()

    # VLCプレイヤーの設定
    instance = vlc.Instance("--no-video-title-show", "--input-repeat=999")
    player = instance.media_player_new()
    video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))]
    current_index = 0

    def play_video(index):
        media = instance.media_new(os.path.join(video_folder, video_files[index]))
        player.set_media(media)
        player.set_hwnd(root.winfo_id())  # Windows用。Linuxなら player.set_xwindow()
        player.play()

    def next_video(event=None):
        nonlocal current_index
        current_index = (current_index + 1) % len(video_files)
        play_video(current_index)

    def exit_program(event=None):
        player.stop()
        root.destroy()

    root.bind("<space>", next_video)
    root.bind("<Escape>", exit_program)

    play_video(current_index)
    root.mainloop()
