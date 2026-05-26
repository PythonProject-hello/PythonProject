import tkinter as tk
from core.monitor import get_stats
from core.character import get_mood, MOOD_LABEL
from config.settings import REFRESH_INTERVAL, MOOD_THRESHOLDS
from ui.settings_window import SettingsWindow

RESOURCE_LABELS = {
    "cpu":     "CPU",
    "ram":     "RAM",
    "disk":    "디스크",
    "network": "네트워크",
    "battery": "배터리",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("시스템 모니터")
        self.resizable(False, False)

        # 자원 표시 여부
        self.visibility = {
            "cpu":     tk.BooleanVar(value=True),
            "ram":     tk.BooleanVar(value=True),
            "disk":    tk.BooleanVar(value=False),
            "network": tk.BooleanVar(value=False),
            "battery": tk.BooleanVar(value=False),
        }

        # 임계값 (설정창에서 수정 가능)
        self.thresholds = dict(MOOD_THRESHOLDS)

        self._stat_labels = {}
        self.rebuild_ui()
        self._update()

    def rebuild_ui(self):
        for w in self.winfo_children():
            w.destroy()
        self._stat_labels = {}
        self._build_ui()

    def _build_ui(self):
        for key, label in RESOURCE_LABELS.items():
            if not self.visibility[key].get():
                continue
            lbl = tk.Label(self, text=f"{label} : -", font=("Consolas", 14))
            lbl.pack(padx=20, pady=(16, 2))
            self._stat_labels[key] = lbl

        self.lbl_mood = tk.Label(self, text="", font=("Consolas", 16))
        self.lbl_mood.pack(padx=20, pady=(8, 4))

        tk.Button(self, text="설정", command=self._open_settings).pack(pady=(4, 16))

    def _open_settings(self):
        SettingsWindow(self)

    def _update(self):
        stats = get_stats()
        mood  = get_mood(stats, self.thresholds)

        for key, lbl in self._stat_labels.items():
            val = stats.get(key)
            if val is None:
                lbl.config(text=f"{RESOURCE_LABELS[key]} : N/A")
            else:
                lbl.config(text=f"{RESOURCE_LABELS[key]} : {val:5.1f}%")

        self.lbl_mood.config(text=MOOD_LABEL[mood])
        self.after(REFRESH_INTERVAL * 1000, self._update)
