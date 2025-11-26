import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import imageio.v2 as iio  # ★ 追加：動画読み込み用
import os
import random
import time
from datetime import datetime
import utils.fetch_weather_from_tenkijp as fetch_weather_from_tenkijp
import screens.video_mode_setting_screen as video_mode_setting_screen

class SimpleVideoWeatherScreen:
    def __init__(self):
        self.video_path = "./videos"  # 動画フォルダ
        self.video_files = [f for f in os.listdir(self.video_path)
                            if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
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

        # 動画と表示更新を開始
        self.play_random_video()
        self.update_weather()
        self.update_display()
        self.root.mainloop()

    def play_random_video(self):
        """ランダムな動画ファイルを選んで reader を準備"""
        if not self.video_files:
            messagebox.showerror("Error", "動画ファイルが見つかりません")
            self.root.destroy()
            return

        random_file = random.choice(self.video_files)
        path = os.path.join(self.video_path, random_file)

        try:
            # imageio の VideoReader を作成
            self.video_reader = iio.get_reader(path)
        except Exception as e:
            messagebox.showerror("Error", f"動画を開けません: {path}\n{e}")
            self.root.destroy()
            return

        # メタデータから fps を取得（無ければ 30fps）
        meta = self.video_reader.get_meta_data()
        fps = meta.get('fps', 30) or 30
        self.frame_interval = 1.0 / fps

        # フレームイテレータを準備
        self.frame_iterator = iter(self.video_reader)

    def update_display(self):
        """フレーム更新＋時刻・天気更新"""
        frame = None
        try:
            # 次のフレームを取得
            frame = next(self.frame_iterator)
        except StopIteration:
            # 動画が終わったら最初から再生
            try:
                self.frame_iterator = iter(self.video_reader)
                frame = next(self.frame_iterator)
            except Exception:
                frame = None

        if frame is not None:
            # frame: (H, W, 3) ndarray, RGB 想定
            pil_image = Image.fromarray(frame)

            # 画面サイズにリサイズ
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            pil_image = pil_image.resize((screen_w, screen_h))

            photo = ImageTk.PhotoImage(pil_image)
            self.video_label.configure(image=photo)
            self.video_label.image = photo
            self.overlay.lift()

        # 時刻・日付更新
        self.update_time_labels()

        # 天気は1時間ごとに更新
        if time.time() - self.last_weather_update > 3600:
            self.update_weather()

        # 次フレームのスケジュール
        delay_ms = int(self.frame_interval * 1000)
        self.root.after(delay_ms, self.update_display)

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
        try:
            if hasattr(self, 'video_reader'):
                self.video_reader.close()
        except Exception:
            pass
        self.root.destroy()
        video_mode_setting_screen.create_screen()

def create_screen():
    try:
        SimpleVideoWeatherScreen()
    except Exception as e:
        messagebox.showerror("Error", f"起動エラー: {e}")
        video_mode_setting_screen.create_screen()
