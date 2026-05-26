import tkinter as tk
from core.monitor import get_stats
from core.character import get_mood, MOOD_LABEL
from config.settings import REFRESH_INTERVAL


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("시스템 모니터")
        self.resizable(False, False)
        self._build_ui()
        self._update()

    def _build_ui(self):
        self.lbl_cpu  = tk.Label(self, text="CPU : -", font=("Consolas", 14))
        self.lbl_ram  = tk.Label(self, text="RAM : -", font=("Consolas", 14))
        self.lbl_mood = tk.Label(self, text="",        font=("Consolas", 16))

        self.lbl_cpu .pack(padx=20, pady=(20, 4))
        self.lbl_ram .pack(padx=20, pady=4)
        self.lbl_mood.pack(padx=20, pady=(4, 20))

    def _update(self):
        stats = get_stats()
        mood  = get_mood(stats)

        self.lbl_cpu .config(text=f"CPU : {stats['cpu']:5.1f}%")
        self.lbl_ram .config(text=f"RAM : {stats['ram']:5.1f}%")
        self.lbl_mood.config(text=MOOD_LABEL[mood])

        self.after(REFRESH_INTERVAL * 1000, self._update)
