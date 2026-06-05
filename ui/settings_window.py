import tkinter as tk
from tkinter import ttk
import psutil
from config.settings import RESOURCES, SLIDER_DEFAULTS


def _battery_available():
    return psutil.sensors_battery() is not None


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

    def _tab_resources(self, parent):
        frame = tk.Frame(parent)
        has_battery = _battery_available()

        for key, label, _, _fmt in RESOURCES:
            if key in ("battery", "charging") and not has_battery:
                continue
            tk.Checkbutton(frame, text=label, variable=self.app.visibility[key],
                           font=("Consolas", 11)).pack(anchor="w", padx=16, pady=3)

        return frame

    def _tab_sliders(self, parent):
        frame = tk.Frame(parent)

        labels = {key: label for key, label, _, _fmt in RESOURCES}
        for key in SLIDER_DEFAULTS:
            var = self.app.show_slider.get(key)
            if var is None:
                continue
            lbl = labels.get(key, key)
            tk.Checkbutton(frame, text=f"{lbl} 슬라이더 표시", variable=var,
                           font=("Consolas", 11)).pack(anchor="w", padx=16, pady=3)

        return frame

    def _apply(self):
        self.app.rebuild_ui()
        self.destroy()
