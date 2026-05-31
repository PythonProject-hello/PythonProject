import tkinter as tk
from tkinter import ttk
from core.monitor import project_data as get_stats
from core.character import get_dialogue
from config.settings import REFRESH_INTERVAL, MOOD_THRESHOLDS, RESOURCES, SLIDER_DEFAULTS


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("시스템 모니터")
        self.resizable(False, False)

        self.visibility = {
            key: tk.BooleanVar(value=default)
            for key, _, default, _fmt in RESOURCES
        }
        self.show_slider = {
            key: tk.BooleanVar(value=val)
            for key, val in SLIDER_DEFAULTS.items()
        }
        self.thresholds = dict(MOOD_THRESHOLDS)

        self._stat_labels = {}
        self._stat_bars   = {}
        self.rebuild_ui()
        self._update()

    def rebuild_ui(self):
        for w in self.winfo_children():
            w.destroy()
        self._stat_labels = {}
        self._stat_bars   = {}
        self._build_ui()

    def _build_ui(self):
        for key, label, _, _fmt in RESOURCES:
            if not self.visibility[key].get():
                continue

            lbl = tk.Label(self, text=f"{label} : -", font=("Consolas", 14))
            lbl.pack(padx=20, pady=(16, 2))
            self._stat_labels[key] = lbl

            if key in self.show_slider and self.show_slider[key].get():
                bar = ttk.Progressbar(self, length=200, maximum=100)
                bar.pack(padx=20, pady=(0, 4))
                self._stat_bars[key] = bar

        self.lbl_mood = tk.Label(self, text="", font=("Consolas", 16))
        self.lbl_mood.pack(padx=20, pady=(8, 4))

        tk.Button(self, text="설정", command=self._open_settings).pack(pady=(4, 16))

    def _open_settings(self):
        from ui.settings_window import SettingsWindow
        SettingsWindow(self)

    def _update(self):
        stats = get_stats()
        dialogue = get_dialogue(stats, self.thresholds)

        for key, label, _, fmt in RESOURCES:
            lbl = self._stat_labels.get(key)
            if lbl is None:
                continue
            val = stats.get(key)
            if val is None:
                text = f"{label} : N/A"
            elif fmt == "bool":
                text = f"{label} : {'충전중' if val else '미충전'}"
            else:
                text = f"{label} : {fmt.format(val)}"
            lbl.config(text=text)

            bar = self._stat_bars.get(key)
            if bar is not None and val is not None:
                bar["value"] = val

        self.lbl_mood.config(text=dialogue)
        self.after(REFRESH_INTERVAL * 1000, self._update)
