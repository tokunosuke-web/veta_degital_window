import tkinter as tk
from time import strftime, localtime
import utils.fetch_weather_from_tenkijp as fetch_weather_from_tenkijp

# 表示設定
BOTTOM_FONT_SIZE = 36
TEXT_COLOR = "white"
BACKGROUND_COLOR = "black"
OVERLAY_BG = "#00000080"  # 半透明黒（#RRGGBBAA形式）

class OverlayDisplayScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Overlay Display")
        self.root.configure(background=BACKGROUND_COLOR)
        self.root.attributes("-fullscreen", True)

        # Canvasを使って上に重ねる
        self.canvas = tk.Canvas(self.root, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 半透明バーを作る
        self.overlay_rect = None
        self.text_item = None
        self.create_overlay()

        # 情報更新
        self.weather_text = "Loading weather..."
        self.update_display()
        self.update_weather()

    def create_overlay(self):
        """下部に半透明バー＋テキストを作成"""
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        bar_height = 100

        # 半透明の黒いバー
        self.overlay_rect = self.canvas.create_rectangle(
            0, h - bar_height, w, h,
            fill=OVERLAY_BG,
            outline=""
        )

        # テキスト（中央下）
        self.text_item = self.canvas.create_text(
            w // 2,
            h - bar_height // 2,
            text="Loading...",
            fill=TEXT_COLOR,
            font=("calibri", BOTTOM_FONT_SIZE, "bold"),
            anchor="center"
        )

    def update_display(self):
        """現在時刻と天気をまとめて更新"""
        current_time = strftime('%H:%M:%S')
        current_date = strftime('%Y-%m-%d %a', localtime())
        display_text = f"{current_date}　{current_time}　　{self.weather_text}"
        self.canvas.itemconfig(self.text_item, text=display_text)
        self.root.after(1000, self.update_display)

    def update_weather(self):
        """天気データを1時間ごとに取得"""
        forecast_data = fetch_weather_from_tenkijp.get_precipitation_forecast()
        if forecast_data and "weather_data" in forecast_data:
            today = forecast_data["weather_data"][0]
            self.weather_text = f"{today['weather_icon']}  ↑{today['high_temp']}°  ↓{today['low_temp']}°"
        else:
            self.weather_text = "天気情報取得失敗"
        self.update_display()
        self.root.after(3600 * 1000, self.update_weather)


def create_screen():
    root = tk.Tk()
    OverlayDisplayScreen(root)
    root.mainloop()
