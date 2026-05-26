import tkinter as tk
from tkinter import ttk
import psutil
from config.settings import MOOD_THRESHOLDS


def _battery_available():
    return psutil.sensors_battery() is not None


RESOURCES = [
    ("cpu",     "CPU"),
    ("ram",     "RAM"),
    ("disk",    "디스크"),
    ("network", "네트워크"),
    ("battery", "배터리"),
]

SLIDERS = [
    ("tired_cpu",  "CPU 피로 기준",   0, 100),
    ("tired_ram",  "RAM 피로 기준",   0, 100),
    ("panic_cpu",  "CPU 패닉 기준",   0, 100),
    ("panic_ram",  "RAM 패닉 기준",   0, 100),
]


class SettingsWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("설정")
        self.resizable(False, False)
        self.grab_set()

        self._slider_vars = {}
        self._build()

    def _build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(padx=12, pady=12, fill="both")

        notebook.add(self._tab_resources(notebook), text="자원 표시")
        notebook.add(self._tab_sliders(notebook),   text="슬라이더 설정")

        tk.Button(self, text="적용", width=10, command=self._apply).pack(pady=(0, 12))

    # ── 탭 1: 자원 On/Off ────────────────────────────────────────────
    def _tab_resources(self, parent):
        frame = tk.Frame(parent)
        has_battery = _battery_available()

        for key, label in RESOURCES:
            if key == "battery" and not has_battery:
                continue  # 배터리 없는 PC면 항목 자체를 숨김

            var = self.app.visibility[key]
            tk.Checkbutton(frame, text=label, variable=var,
                           font=("Consolas", 11)).pack(anchor="w", padx=16, pady=3)

        return frame

    # ── 탭 2: 슬라이더 ───────────────────────────────────────────────
    def _tab_sliders(self, parent):
        frame = tk.Frame(parent)

        for key, label, lo, hi in SLIDERS:
            var = tk.IntVar(value=self.app.thresholds[key])
            self._slider_vars[key] = var

            row = tk.Frame(frame)
            row.pack(fill="x", padx=16, pady=4)

            tk.Label(row, text=f"{label}:", font=("Consolas", 10), width=16,
                     anchor="w").pack(side="left")
            tk.Scale(row, from_=lo, to=hi, orient="horizontal",
                     variable=var, length=160).pack(side="left")
            tk.Label(row, textvariable=var, font=("Consolas", 10),
                     width=4).pack(side="left")

        return frame

    # ── 적용 ─────────────────────────────────────────────────────────
    def _apply(self):
        for key, var in self._slider_vars.items():
            self.app.thresholds[key] = var.get()
        self.app.rebuild_ui()
        self.destroy()
