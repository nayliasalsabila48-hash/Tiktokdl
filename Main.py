import subprocess, os, threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex("#0a0a0a")

class TikTokDL(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=15, spacing=10, **kwargs)
        self.add_widget(Label(text="[b][color=FF0050]TikTok[/color][color=00F2EA]DL Pro[/color][/b]",
            markup=True, font_size=28, size_hint_y=None, height=50))
        self.add_widget(Label(text="No Watermark Downloader",
            color=get_color_from_hex("#888888"), size_hint_y=None, height=25))
        self.url_input = TextInput(hint_text="Paste URL TikTok di sini...",
            size_hint_y=None, height=50,
            background_color=get_color_from_hex("#1a1a1a"),
            foreground_color=[1,1,1,1],
            hint_text_color=[0.4,0.4,0.4,1], padding=[10,12])
        self.add_widget(self.url_input)
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=8)
        btn_video = Button(text="Download Video",
            background_color=get_color_from_hex("#FF0050"), bold=True)
        btn_audio = Button(text="Download MP3",
            background_color=get_color_from_hex("#00F2EA"),
            bold=True, color=[0,0,0,1])
        btn_video.bind(on_press=lambda x: self.download(False))
        btn_audio.bind(on_press=lambda x: self.download(True))
        btn_layout.add_widget(btn_video)
        btn_layout.add_widget(btn_audio)
        self.add_widget(btn_layout)
        self.status = Label(text="Siap download...",
            color=get_color_from_hex("#00FF88"),
            size_hint_y=None, height=35)
        self.add_widget(self.status)
        sv = ScrollView()
        self.log = Label(text="", markup=True, valign="top", halign="left",
            color=get_color_from_hex("#cccccc"), font_size=12)
        self.log.bind(width=lambda *x: self.log.setter("text_size")(self.log,(self.log.width,None)))
        sv.add_widget(self.log)
        self.add_widget(sv)

    def download(self, audio_only):
        url = self.url_input.text.strip()
        if not url:
            self.status.text = "Masukkan URL dulu!"
            return
        self.status.text = "Downloading..."
        self.status.color = get_color_from_hex("#FFD700")
        threading.Thread(target=self._do_download,
            args=(url, audio_only), daemon=True).start()

    def _do_download(self, url, audio_only):
        from pathlib import Path
        save = Path("/sdcard/TikTokDL")
        save.mkdir(parents=True, exist_ok=True)
        if audio_only:
            cmd = ["yt-dlp","-x","--audio-format","mp3",
                "-o",str(save/"%(title)s.%(ext)s"),url]
        else:
            cmd = ["yt-dlp","-f","best[ext=mp4]/best",
                "--no-playlist","-o",str(save/"%(title)s.%(ext)s"),url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                self.status.text = "Berhasil! Cek folder TikTokDL"
                self.status.color = get_color_from_hex("#00FF88")
                self.log.text += "[color=00FF88]Download berhasil![/color]\n"
            else:
                self.status.text = "Gagal! Cek URL"
                self.status.color = get_color_from_hex("#FF4444")
                self.log.text += f"[color=FF4444]Error: {result.stderr[-200:]}[/color]\n"
        except Exception as e:
            self.status.text = f"Error: {str(e)}"

class TikTokDLApp(App):
    def build(self):
        return TikTokDL()

if __name__ == "__main__":
    TikTokDLApp().run()
