import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import random
import time
from datetime import datetime
import utils.fetch_weather_from_tenkijp as fetch_weather_from_tenkijp
import screens.video_mode_setting_screen as video_mode_setting_screen

class SimpleVideoWeatherScreen:
    def __init__(self):
        self.video_path = "./videos"  # 動画フォルダ
        self.video_files = [f for f in os.listdir(self.video_path) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        self.weather_data = None
        self.last_weather_update = 0

        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

        # 背景動画
        self.video_label = tk.Label(self.root, bg='black')
        self.video_label.pack(expand=True, fill='both')

        # 下部オーバーレイ
        self.overlay = tk.Frame(self.root, bg='black')
        self.overlay.place(relx=0, rely=0.85, relwidth=1.0, relheight=0.15)

        self.time_label = tk.Label(self.overlay, fg='white', bg='black', font=('Arial', 60, 'bold'))
        self.time_label.pack(side='left', padx=40)

        self.date_label = tk.Label(self.overlay, fg='white', bg='black', font=('Arial', 30))
        self.date_label.pack(side='left')

        self.weather_label = tk.Label(self.overlay, fg='white', bg='black', font=('Arial', 24))
        self.weather_label.pack(side='right', padx=40)

        self.root.bind('<Escape>', lambda e: self.close_window())

        self.play_random_video()
        self.update_weather()
        self.update_display()
        self.root.mainloop()

    def play_random_video(self):
        if not self.video_files:
            messagebox.showerror("Error", "動画ファイルが見つかりません")
            self.root.destroy()
            return

        random_file = random.choice(self.video_files)
        path = os.path.join(self.video_path, random_file)
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"動画を開けません: {path}")
            self.root.destroy()
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_interval = 1.0 / fps if fps > 0 else 1.0 / 30

    def update_display(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            frame_resized = pil_image.resize((screen_w, screen_h))
            photo = ImageTk.PhotoImage(frame_resized)
            self.video_label.configure(image=photo)
            self.video_label.image = photo
            self.overlay.lift()

        self.update_time_labels()
        if time.time() - self.last_weather_update > 3600:  # 1時間ごとに更新
            self.update_weather()
        self.root.after(int(self.frame_interval * 1000), self.update_display)

    def update_time_labels(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text="  " + now.strftime("%Y-%m-%d (%a)"))

    def update_weather(self):
        try:
            data = fetch_weather_from_tenkijp.get_precipitation_forecast()
            if isinstance(data, dict):
                text = data.get("today", {}).get("summary", "天気情報なし")
            else:
                text = str(data)
            self.weather_label.config(text=text[:50])
        except Exception as e:
            print("天気データ取得エラー:", e)
            self.weather_label.config(text="天気情報取得中...")
        self.last_weather_update = time.time()

    def close_window(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        self.root.destroy()
        video_mode_setting_screen.create_screen()

def create_screen():
    try:
        SimpleVideoWeatherScreen()
    except Exception as e:
        messagebox.showerror("Error", f"起動エラー: {e}")
        video_mode_setting_screen.create_screen()
