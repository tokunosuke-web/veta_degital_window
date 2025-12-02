import pygame
import imageio.v2 as iio
import os
import random
import numpy as np
from time import time, strftime, localtime

# --- 設定 ---
VIDEO_PATH = "videos"  # 動画フォルダパス（適宜変更）
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.MOV', '.mkv')
DATE_FONT_SIZE = 28
TIME_FONT_SIZE = 70

class VideoClockDisplay:
    def __init__(self):
        self.video_files = [f for f in os.listdir(VIDEO_PATH) if f.endswith(VIDEO_EXTENSIONS)]
        self.running = True
        self.initialize_display()

    def initialize_display(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_size = (self.screen.get_width(), self.screen.get_height())
        self.date_font = pygame.font.SysFont('calibri', DATE_FONT_SIZE, bold=True)
        self.time_font = pygame.font.SysFont('calibri', TIME_FONT_SIZE, bold=True)
        self.play_random_video()

    def play_random_video(self):
        self.current_video_path = os.path.join(VIDEO_PATH, random.choice(self.video_files))
        self.video_reader = iio.get_reader(self.current_video_path)
        self.frame_iterator = iter(self.video_reader)
        fps = self.video_reader.get_meta_data().get("fps", 30) or 30
        clock = pygame.time.Clock()
        frame_interval = 1.0 / fps
        last_frame_time = time()

        while self.running:
            current_time = time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]):
                    self.running = False

            if current_time - last_frame_time >= frame_interval:
                self.update_frame()
                last_frame_time = current_time

            clock.tick(int(fps))

        pygame.quit()

    def update_frame(self):
        try:
            frame = next(self.frame_iterator)
        except StopIteration:
            self.video_reader.close()
            self.video_reader = iio.get_reader(self.current_video_path)
            self.frame_iterator = iter(self.video_reader)
            frame = next(self.frame_iterator)

        frame_surface = pygame.surfarray.make_surface(np.rot90(frame))
        scale_ratio = max(self.screen_size[0] / frame_surface.get_width(), self.screen_size[1] / frame_surface.get_height())
        new_size = (int(frame_surface.get_width() * scale_ratio), int(frame_surface.get_height() * scale_ratio))
        frame_surface = pygame.transform.scale(frame_surface, new_size)
        offset_x = (new_size[0] - self.screen_size[0]) // 2
        offset_y = (new_size[1] - self.screen_size[1]) // 2
        clip_area = pygame.Rect(offset_x, offset_y, *self.screen_size)
        self.screen.blit(frame_surface, (0, 0), area=clip_area)

        self.display_datetime_overlay()
        pygame.display.flip()

    def display_datetime_overlay(self):
        current_date = strftime('%Y-%m-%d %A', localtime())
        current_time = strftime('%H:%M:%S', localtime())
        date_surface = self.date_font.render(current_date, True, (255, 255, 255))
        time_surface = self.time_font.render(current_time, True, (255, 255, 255))
        self.screen.blit(date_surface, (self.screen_size[0] // 3.5, self.screen_size[1] - 300))
        self.screen.blit(time_surface, (self.screen_size[0] // 3.5, self.screen_size[1] - 150))


if __name__ == "__main__":
    VideoClockDisplay()
