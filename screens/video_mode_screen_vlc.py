import tkinter as tk
import screens.video_mode_setting_screen as video_mode_setting_screen
import utils.settings_manager as settings_manager
import os
import random
from datetime import datetime
from tkinter import messagebox
from time import strftime, localtime, time
import pygame
import imageio.v2 as iio
import numpy as np

DATE_FONT_SIZE = 80
TIME_FONT_SIZE = 160

class VideoModeScreenPygame:
    def __init__(self):
        self.image_brightness = 1.0
        self.current_video_index = 0
        self.is_playing = False
        self.last_video_change_time = time()
        self.running = True

        self.initialize_settings()
        self.init_pygame_screen()      # ← 画面は一度だけ作る
        self.load_new_video()          # ← 最初の動画を読み込み
        self.main_loop()               # ← メインループ開始

    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.video_path = settings.get('video_path')
        self.interval = int(settings.get('interval'))
        self.automatic_brightness = settings.get('automatic_brightness')
        self.show_time = True
        self.show_weather = False
        self.show_train_schedule = False
        self.sound_path = ""
        self.sound_mode = "0"
        self.preserve_quality = settings.get('preserve_quality', True)
        self.play_video_audio = settings.get('play_video_audio', False)

        self.video_files = [
            f for f in os.listdir(self.video_path)
            if f.endswith(('.mp4', '.avi', '.mov', '.MOV', '.mkv'))
        ]

    # 画面（ウィンドウ）は一度だけ作る
    def init_pygame_screen(self):
        pygame.init()
        pygame.display.set_caption("Video Display App")
        self.screen = pygame.display.set_mode(
            (pygame.display.Info().current_w, pygame.display.Info().current_h),
            pygame.FULLSCREEN
        )
        self.screen_size = (self.screen.get_width(), self.screen.get_height())
        self.scale_ratio = None

    # 新しい動画を読み込む処理
    def load_new_video(self):
        random_video_path = self.make_random_file_path(self.video_path, self.video_files)
        self.current_video_path = random_video_path

        # 前の動画を閉じる（あれば）
        if hasattr(self, "video_reader"):
            try:
                self.video_reader.close()
            except Exception:
                pass

        try:
            self.video_reader = iio.get_reader(random_video_path)
        except Exception as e:
            print(f"動画ファイルを開けません: {random_video_path} / {e}")
            return

        meta = self.video_reader.get_meta_data()
        fps = meta.get("fps", 30) or 30
        self.fps = fps
        self.frame_interval = 1.0 / fps

        size = meta.get("size", None)
        if size:
            self.video_width, self.video_height = size
        else:
            self.video_width, self.video_height = 0, 0

        # 必要ならここで自動判定にしてもOK
        self.rotation_needed = 90
        self.flip_needed = False

        self.frame_iterator = iter(self.video_reader)
        self.scale_ratio = None

        # ★ここで「動画切り替えの起点時間」を更新する
        self.last_video_change_time = time()

    # メインループ（画面は閉じず、動画だけ差し替える）
    def main_loop(self):
        clock = pygame.time.Clock()
        last_frame_time = time()

        while self.running:
            current_time = time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]):
                    self.close_window()

            # フレーム更新
            if current_time - last_frame_time >= self.frame_interval:
                self.update_video_frame()
                last_frame_time = current_time

            # interval 秒たったら次の動画を読み込む
            if current_time - self.last_video_change_time >= self.interval:
                self.load_new_video()

            clock.tick(int(self.fps))

    def update_video_frame(self):
        try:
            frame = next(self.frame_iterator)
        except StopIteration:
            # 動画が最後まで行ったらループさせる
            self.video_reader.close()
            self.video_reader = iio.get_reader(self.current_video_path)
            self.frame_iterator = iter(self.video_reader)
            frame = next(self.frame_iterator)

        frame = self.correct_rotation(frame)
        frame_surface = pygame.surfarray.make_surface(frame)

        if not self.scale_ratio:
            self.scale_ratio = max(
                self.screen_size[0] / frame_surface.get_width(),
                self.screen_size[1] / frame_surface.get_height()
            )

        new_size = (int(frame_surface.get_width() * self.scale_ratio),
                    int(frame_surface.get_height() * self.scale_ratio))

        if self.preserve_quality:
            frame_surface = pygame.transform.smoothscale(frame_surface, new_size)
        else:
            frame_surface = pygame.transform.scale(frame_surface, new_size)

        offset_x = (new_size[0] - self.screen_size[0]) // 2
        offset_y = (new_size[1] - self.screen_size[1]) // 2

        clip_area = pygame.Rect(offset_x, offset_y, *self.screen_size)
        self.screen.blit(frame_surface, (0, 0), area=clip_area)

        if self.image_brightness < 1.0:
            overlay = pygame.Surface(self.screen_size)
            overlay.fill((0, 0, 0))
            overlay.set_alpha(int(255 - self.image_brightness * 255))
            self.screen.blit(overlay, (0, 0))

        if self.show_time:
            self.show_clock()

        pygame.display.flip()

    def show_clock(self):
        current_date = strftime('%Y-%m-%d %A', localtime())
        current_time = strftime('%H:%M:%S', localtime())
        if not hasattr(self, 'date_font'):
            self.date_font = pygame.font.SysFont('calibri', DATE_FONT_SIZE, bold=True)
            self.time_font = pygame.font.SysFont('calibri', TIME_FONT_SIZE, bold=True)

        date_surface = self.date_font.render(current_date, True, (255, 255, 255))
        time_surface = self.time_font.render(current_time, True, (255, 255, 255))

        self.screen.blit(date_surface, (self.screen_size[0] // 13.5, 800))
        self.screen.blit(time_surface, (self.screen_size[0] // 13.5, 900))

    def correct_rotation(self, frame):
        rotation = self.rotation_needed
        if rotation == 90:
            return np.rot90(frame, k=1)
        elif rotation == 180:
            return np.rot90(frame, k=2)
        elif rotation == 270:
            return np.rot90(frame, k=3)
        return frame

    def make_random_file_path(self, path, files):
        return os.path.join(path, random.choice(files))

    def close_window(self):
        print("終了します")
        self.running = False
        try:
            self.video_reader.close()
        except Exception:
            pass
        pygame.quit()
        video_mode_setting_screen.create_screen()

def create_screen():
    try:
        VideoModeScreenPygame()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        messagebox.showerror("Error", f"動画再生エラー: {e}")
        video_mode_setting_screen.create_screen()
