import tkinter as tk
from tkinter import ttk

from ui.app import BG, PANEL, TEXT, MUTED, BLUE, CARD
from config.settings import MIN_REFRESH_INTERVAL, MAX_REFRESH_INTERVAL, PRESETS, save_settings


class _SliderBar:
    BAR_H   = 6
    KNOB_R  = 9
    PAD_X   = KNOB_R + 2
    TOTAL_H = KNOB_R * 2 + 4

    def __init__(self, parent, variable, from_, to, on_change):
        self.var       = variable
        self.from_     = from_
        self.to        = to
        self.on_change = on_change

        self.canvas = tk.Canvas(parent, height=self.TOTAL_H, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="x", pady=(4, 0))
        self.canvas.bind("<Configure>",       self._redraw)
        self.canvas.bind("<Button-1>",        self._click)
        self.canvas.bind("<B1-Motion>",       self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)

    def _ratio(self):
        return (self.var.get() - self.from_) / max(self.to - self.from_, 1)

    def _set_from_x(self, x):
        w      = self.canvas.winfo_width()
        usable = w - self.PAD_X * 2
        ratio  = max(0.0, min(1.0, (x - self.PAD_X) / max(usable, 1)))
        value  = round(self.from_ + ratio * (self.to - self.from_))
        self.var.set(value)
        self.on_change(value)
        self._redraw()

    def _click(self, e):   self._set_from_x(e.x)
    def _drag(self, e):    self._set_from_x(e.x)
    def _release(self, e): self._set_from_x(e.x)

    def _redraw(self, _=None):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 1:
            return
        cy     = self.TOTAL_H // 2
        x0     = self.PAD_X
        x1     = w - self.PAD_X
        fill_x = x0 + int((x1 - x0) * self._ratio())

        c.create_line(x0, cy, x1, cy, fill="#3a414b", width=self.BAR_H, capstyle="round")
        if fill_x > x0:
            c.create_line(x0, cy, fill_x, cy, fill=BLUE, width=self.BAR_H, capstyle="round")
        r = self.KNOB_R
        c.create_oval(fill_x - r, cy - r, fill_x + r, cy + r, fill=BLUE, outline="#0f1115", width=2)


class SettingsWindow:
    def __init__(self, app):
        self.app = app

        win = tk.Toplevel(app.root)
        self.win = win
        win.title("설정")
        win.geometry("430x560")
        win.configure(bg=BG)
        win.resizable(False, False)

        def on_close():
            app.settings_win = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close)

        # 스크롤 가능한 내부 영역
        scroll_canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
        scrollbar     = ttk.Scrollbar(win, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(scroll_canvas, bg=BG)
        win_id = scroll_canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_resize(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def _on_canvas_resize(e):
            scroll_canvas.itemconfig(win_id, width=e.width)

        inner.bind("<Configure>", _on_inner_resize)
        scroll_canvas.bind("<Configure>", _on_canvas_resize)

        # 마우스 휠 스크롤
        def _on_mousewheel(e):
            scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        win.bind("<MouseWheel>", _on_mousewheel)

        # 임시 변수 (저장 전까지 app에 반영 안 됨)
        tmp_show     = {k: tk.BooleanVar(value=v.get()) for k, v in app.show_vars.items()}
        tmp_cpu      = tk.IntVar(value=app.cpu_hot.get())
        tmp_ram      = tk.IntVar(value=app.ram_hot.get())
        tmp_bat      = tk.IntVar(value=app.battery_low.get())
        tmp_disk     = tk.IntVar(value=app.disk_hot.get())
        tmp_interval = tk.IntVar(value=app.refresh_interval.get())
        tmp_auto     = tk.BooleanVar(value=app.auto_refresh.get())

        # --- 자원 표시 체크박스 ---
        tk.Label(inner, text="컴퓨팅 자원 설정", font=("Apple SD Gothic Neo", 22, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=28, pady=(26, 6))
        tk.Label(inner, text="표시할 정보와 캐릭터 반응 기준을 조절합니다.", font=("Apple SD Gothic Neo", 12, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=28, pady=(0, 14))

        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure("Dark.TCheckbutton", background=PANEL, foreground=TEXT, font=("Apple SD Gothic Neo", 14, "bold"))
        style.map("Dark.TCheckbutton", background=[("active", PANEL)], foreground=[("active", TEXT)])

        box = tk.Frame(inner, bg=PANEL, padx=18, pady=14)
        box.pack(fill="x", padx=26, pady=(0, 16))
        for key, text in [
            ("cpu",     "CPU 사용률"),
            ("ram",     "메모리 사용량"),
            ("disk",    "저장 공간"),
            ("battery", "배터리"),
        ]:
            ttk.Checkbutton(box, text=text, variable=tmp_show[key], style="Dark.TCheckbutton").pack(anchor="w", pady=5)

        # --- 프리셋 ---
        preset_frame = tk.Frame(inner, bg=BG)
        preset_frame.pack(fill="x", padx=28, pady=(4, 0))
        tk.Label(preset_frame, text="프리셋", bg=BG, fg=MUTED, font=("Apple SD Gothic Neo", 12, "bold")).pack(anchor="w")

        btn_row = tk.Frame(preset_frame, bg=BG)
        btn_row.pack(fill="x", pady=(4, 0))

        def apply_preset(values):
            set_cpu(values["cpu_hot"])
            set_ram(values["ram_hot"])
            set_bat(values["battery_low"])
            set_disk(values["disk_hot"])

        for name, values in PRESETS.items():
            tk.Button(
                btn_row, text=name, command=lambda v=values: apply_preset(v),
                font=("Apple SD Gothic Neo", 11, "bold"), bg=CARD, fg=TEXT, bd=0,
                padx=14, pady=6, cursor="hand2",
            ).pack(side="left", padx=(0, 8))

        # --- 임계값 슬라이더 ---
        set_cpu  = self._make_slider(inner, "CPU 힘듦 기준",     tmp_cpu,  40, 95, "%")
        set_ram  = self._make_slider(inner, "RAM 과부하 기준",    tmp_ram,  50, 95, "%")
        set_bat  = self._make_slider(inner, "배터리 배고픔 기준", tmp_bat,   5, 60, "%")
        set_disk = self._make_slider(inner, "디스크 배부름 기준", tmp_disk, 20, 95, "%")

        self._make_slider(inner, "갱신 주기", tmp_interval, MIN_REFRESH_INTERVAL, MAX_REFRESH_INTERVAL, "초")

        ttk.Checkbutton(inner, text="자동 새로고침", variable=tmp_auto, style="Dark.TCheckbutton").pack(anchor="w", padx=30, pady=(14, 0))

        # --- 저장 버튼 ---
        def save():
            for k, v in tmp_show.items():
                app.show_vars[k].set(v.get())
            app.cpu_hot.set(tmp_cpu.get())
            app.ram_hot.set(tmp_ram.get())
            app.battery_low.set(tmp_bat.get())
            app.disk_hot.set(tmp_disk.get())
            interval_changed = tmp_interval.get() != app.refresh_interval.get()
            app.refresh_interval.set(tmp_interval.get())
            prev_auto = app.auto_refresh.get()
            app.auto_refresh.set(tmp_auto.get())
            if tmp_auto.get() != prev_auto or (tmp_auto.get() and interval_changed):
                app.toggle_auto_refresh()

            save_settings({
                **{k: v.get() for k, v in app.show_vars.items()},
                "cpu_hot":          app.cpu_hot.get(),
                "ram_hot":          app.ram_hot.get(),
                "battery_low":      app.battery_low.get(),
                "disk_hot":         app.disk_hot.get(),
                "refresh_interval": app.refresh_interval.get(),
                "auto_refresh":     app.auto_refresh.get(),
            })

            app.settings_win = None
            win.destroy()
            app.refresh()

        tk.Button(inner, text="저장", command=save, font=("Apple SD Gothic Neo", 14, "bold"), bg=BLUE, fg="#071018", bd=0, padx=28, pady=10, cursor="hand2").pack(anchor="e", padx=28, pady=22)

    def _make_slider(self, parent, title, variable, from_, to, suffix):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", padx=28, pady=(10, 4))

        label = tk.Label(frame, text=f"{title}: {variable.get()}{suffix}", bg=BG, fg=TEXT, font=("Apple SD Gothic Neo", 12, "bold"))
        label.pack(anchor="w")

        def on_change(value):
            label.config(text=f"{title}: {value}{suffix}")

        bar = _SliderBar(frame, variable, from_, to, on_change)

        def set_value(value):
            value = max(from_, min(to, value))
            variable.set(value)
            on_change(value)
            bar._redraw()

        return set_value
