    import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
import requests
import os
import json
import re

Window.clearcolor = (0.05, 0.05, 0.1, 1)

API_BASE = "https://tikwm.com/api/"

def get_video_info(url):
    try:
        resp = requests.post(API_BASE, data={"url": url, "hd": 1}, timeout=15)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]
        return None
    except Exception as e:
        return None

def download_file(url, path, progress_callback=None):
    try:
        r = requests.get(url, stream=True, timeout=30)
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total:
                        progress_callback(downloaded / total * 100)
        return True
    except Exception as e:
        return False

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = "15sp"
        with self.canvas.before:
            self.btn_color = Color(0.98, 0.18, 0.38, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class TikTokDLApp(App):
    def build(self):
        self.title = "TikTok DL Pro"
        self.video_info = None
        self.save_path = "/sdcard/Download/TikTokDL"
        os.makedirs(self.save_path, exist_ok=True)

        root = BoxLayout(orientation="vertical", padding=20, spacing=12)

        # Title
        title = Label(
            text="🎵 TikTok DL Pro",
            font_size="26sp",
            bold=True,
            color=(0.98, 0.18, 0.38, 1),
            size_hint_y=None,
            height=50
        )
        root.add_widget(title)

        subtitle = Label(
            text="Download Video & Audio TikTok",
            font_size="13sp",
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=None,
            height=25
        )
        root.add_widget(subtitle)

        # URL Input
        url_label = Label(
            text="Paste Link TikTok:",
            font_size="13sp",
            color=(0.9, 0.9, 1, 1),
            size_hint_y=None,
            height=28,
            halign="left",
            text_size=(Window.width - 40, None)
        )
        root.add_widget(url_label)

        self.url_input = TextInput(
            hint_text="https://www.tiktok.com/@user/video/...",
            multiline=False,
            size_hint_y=None,
            height=48,
            font_size="13sp",
            background_color=(0.12, 0.12, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.98, 0.18, 0.38, 1),
            hint_text_color=(0.5, 0.5, 0.6, 1),
            padding=[12, 12]
        )
        root.add_widget(self.url_input)

        # Format & Quality Row
        option_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=48, spacing=10)

        self.format_spinner = Spinner(
            text="MP4 (Video)",
            values=["MP4 (Video)", "MP3 (Audio)", "MP4 HD", "MP4 No Watermark"],
            size_hint_x=0.55,
            background_color=(0.12, 0.12, 0.25, 1),
            color=(1, 1, 1, 1),
            font_size="13sp"
        )
        option_row.add_widget(self.format_spinner)

        self.quality_spinner = Spinner(
            text="HD",
            values=["HD", "SD"],
            size_hint_x=0.45,
            background_color=(0.12, 0.12, 0.25, 1),
            color=(1, 1, 1, 1),
            font_size="13sp"
        )
        option_row.add_widget(self.quality_spinner)
        root.add_widget(option_row)

        # Fetch Button
        fetch_btn = RoundedButton(
            text="🔍 Ambil Info Video",
            size_hint_y=None,
            height=48
        )
        fetch_btn.bind(on_press=self.fetch_info)
        root.add_widget(fetch_btn)

        # Info Box (ScrollView)
        scroll = ScrollView(size_hint_y=None, height=130)
        self.info_label = Label(
            text="Info video akan tampil di sini...",
            font_size="12sp",
            color=(0.7, 0.8, 1, 1),
            size_hint_y=None,
            text_size=(Window.width - 50, None),
            markup=True,
            halign="left",
            valign="top"
        )
        self.info_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        scroll.add_widget(self.info_label)
        root.add_widget(scroll)

        # Progress Bar
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=12
        )
        root.add_widget(self.progress)

        # Status Label
        self.status_label = Label(
            text="",
            font_size="12sp",
            color=(0.6, 1, 0.6, 1),
            size_hint_y=None,
            height=28
        )
        root.add_widget(self.status_label)

        # Download Button
        dl_btn = RoundedButton(
            text="⬇️ Download Sekarang",
            size_hint_y=None,
            height=52
        )
        dl_btn.bind(on_press=self.start_download)
        root.add_widget(dl_btn)

        # Footer
        footer = Label(
            text="File disimpan di: /sdcard/Download/TikTokDL",
            font_size="11sp",
            color=(0.4, 0.4, 0.5, 1),
            size_hint_y=None,
            height=28
        )
        root.add_widget(footer)

        return root

    def fetch_info(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.info_label.text = "[color=ff4444]⚠ Masukkan link TikTok dulu![/color]"
            return
        self.info_label.text = "⏳ Mengambil info video..."
        self.status_label.text = ""
        threading.Thread(target=self._fetch_thread, args=(url,), daemon=True).start()

    def _fetch_thread(self, url):
        info = get_video_info(url)
        Clock.schedule_once(lambda dt: self._show_info(info))

    def _show_info(self, info):
        if not info:
            self.info_label.text = "[color=ff4444]❌ Gagal ambil info. Cek link atau koneksi![/color]"
            return
        self.video_info = info
        author = info.get("author", {}).get("nickname", "Unknown")
        desc = info.get("title", "")[:80]
        duration = info.get("duration", 0)
        plays = info.get("play_count", 0)
        likes = info.get("digg_count", 0)
        text = (
            f"[b][color=fe2d55]👤 {author}[/color][/b]\n"
            f"[color=ffffff]{desc}[/color]\n"
            f"⏱ {duration}s  |  ▶ {plays:,}  |  ❤ {likes:,}"
        )
        self.info_label.text = text

    def start_download(self, instance):
        if not self.video_info:
            self.status_label.text = "⚠ Ambil info video dulu!"
            self.status_label.color = (1, 0.5, 0, 1)
            return
        self.progress.value = 0
        fmt = self.format_spinner.text
        quality = self.quality_spinner.text
        threading.Thread(target=self._download_thread, args=(fmt, quality), daemon=True).start()

    def _download_thread(self, fmt, quality):
        info = self.video_info
        Clock.schedule_once(lambda dt: setattr(self.status_label, "text", "⬇ Mengunduh..."))
        Clock.schedule_once(lambda dt: setattr(self.status_label, "color", (0.6, 1, 0.6, 1)))

        author = info.get("author", {}).get("unique_id", "user")
        vid_id = info.get("id", "video")
        filename_base = f"{author}_{vid_id}"

        if "MP3" in fmt:
            dl_url = info.get("music", "")
            ext = "mp3"
        elif "No Watermark" in fmt:
            dl_url = info.get("play", "")
            ext = "mp4"
        elif "HD" in fmt or quality == "HD":
            dl_url = info.get("hdplay", info.get("play", ""))
            ext = "mp4"
        else:
            dl_url = info.get("play", "")
            ext = "mp4"

        if not dl_url:
            Clock.schedule_once(lambda dt: setattr(self.status_label, "text", "❌ URL download tidak ditemukan!"))
            return

        save_file = os.path.join(self.save_path, f"{filename_base}.{ext}")

        def prog_cb(val):
            Clock.schedule_once(lambda dt: setattr(self.progress, "value", val))

        success = download_file(dl_url, save_file, prog_cb)

        if success:
            Clock.schedule_once(lambda dt: setattr(self.status_label, "text", f"✅ Tersimpan: {filename_base}.{ext}"))
            Clock.schedule_once(lambda dt: setattr(self.progress, "value", 100))
        else:
            Clock.schedule_once(lambda dt: setattr(self.status_label, "text", "❌ Download gagal. Coba lagi!"))
            Clock.schedule_once(lambda dt: setattr(self.status_label, "color", (1, 0.3, 0.3, 1)))

if __name__ == "__main__":
    TikTokDLApp().run()
