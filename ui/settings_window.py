import tkinter as tk
from tkinter import ttk

from ui.app import BG, PANEL, TEXT, MUTED, BLUE, CARD, RED
from config.settings import (
    MIN_REFRESH_INTERVAL, MAX_REFRESH_INTERVAL,
    PRESETS, save_settings,
)


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

        # 터치스크린 드래그 스크롤 (toplevel에 바인딩 - bindtags로 모든 자식 위젯의 터치 이벤트도 전달됨)
        def _on_touch_press(e):
            w = e.widget
            # 빈 공간(스크롤 캔버스/프레임/레이블)에서 시작한 터치만 스크롤로 처리.
            # 슬라이더, 체크박스, 입력란, 버튼 등 다른 동작 중에는 스크롤 비활성화.
            if w is scroll_canvas or isinstance(w, (tk.Label, tk.Frame)):
                scroll_canvas._touch_y = e.y_root
            else:
                scroll_canvas._touch_y = None

        def _on_touch_drag(e):
            last_y = getattr(scroll_canvas, "_touch_y", None)
            if last_y is None:
                return
            dy = e.y_root - last_y
            bbox = scroll_canvas.bbox("all")
            if bbox:
                content_h = bbox[3] - bbox[1]
                if content_h > 0:
                    top = scroll_canvas.yview()[0]
                    scroll_canvas.yview_moveto(top - dy / content_h)
            scroll_canvas._touch_y = e.y_root

        def _on_touch_release(_e):
            scroll_canvas._touch_y = None

        win.bind("<ButtonPress-1>",   _on_touch_press,   add="+")
        win.bind("<B1-Motion>",       _on_touch_drag,    add="+")
        win.bind("<ButtonRelease-1>", _on_touch_release, add="+")

        # 임시 변수 (저장 전까지 app에 반영 안 됨)
        tmp_show     = {k: tk.BooleanVar(value=v.get()) for k, v in app.show_vars.items()}
        tmp_cpu      = tk.IntVar(value=app.cpu_hot.get())
        tmp_ram      = tk.IntVar(value=app.ram_hot.get())
        tmp_bat      = tk.IntVar(value=app.battery_low.get())
        tmp_disk     = tk.IntVar(value=app.disk_hot.get())
        tmp_interval = tk.IntVar(value=app.refresh_interval.get())
        tmp_auto     = tk.BooleanVar(value=app.auto_refresh.get())
        tmp_hotkey   = tk.StringVar(value=app.hotkey_key.get())
        tmp_quit_hotkey = tk.StringVar(value=app.quit_hotkey_key.get())
        tmp_alert    = tk.BooleanVar(value=app.alert_enabled.get())

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
        set_cpu  = self._make_slider(inner, "CPU 더움 기준",     tmp_cpu,  5, 95, "%")
        set_ram  = self._make_slider(inner, "RAM 졸림 기준",    tmp_ram,  20, 95, "%")
        set_bat  = self._make_slider(inner, "배터리 배고픔 기준", tmp_bat,   5, 60, "%")
        set_disk = self._make_slider(inner, "디스크 머리아픔 기준", tmp_disk, 20, 95, "%")

        self._make_slider(inner, "갱신 주기", tmp_interval, MIN_REFRESH_INTERVAL, MAX_REFRESH_INTERVAL, "초")

        ttk.Checkbutton(inner, text="자동 새로고침", variable=tmp_auto, style="Dark.TCheckbutton").pack(anchor="w", padx=30, pady=(14, 0))

        # --- 단축키 설정 ---
        tk.Label(inner, text="단축키", font=("Apple SD Gothic Neo", 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=28, pady=(22, 4))
        tk.Label(inner, text="백그라운드 단축키를 설정합니다.", font=("Apple SD Gothic Neo", 11, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=28, pady=(0, 6))

        hotkey_frame = tk.Frame(inner, bg=BG)
        hotkey_frame.pack(anchor="w", padx=28)
        tk.Label(hotkey_frame, text="창 숨기기/보이기: Ctrl + Alt +", bg=BG, fg=TEXT, font=("Apple SD Gothic Neo", 13, "bold")).pack(side="left")

        def _validate_hotkey(value):
            return len(value) <= 1 and (value == "" or value.isalnum())

        vcmd = (inner.register(_validate_hotkey), "%P")
        hotkey_entry = tk.Entry(
            hotkey_frame, textvariable=tmp_hotkey, width=3, justify="center",
            font=("Apple SD Gothic Neo", 13, "bold"), bg=CARD, fg=TEXT,
            insertbackground=TEXT, relief="flat", validate="key", validatecommand=vcmd,
        )
        hotkey_entry.pack(side="left", padx=(8, 0))

        # --- 종료 단축키 ---
        quit_hotkey_frame = tk.Frame(inner, bg=BG)
        quit_hotkey_frame.pack(anchor="w", padx=28, pady=(8, 0))
        tk.Label(quit_hotkey_frame, text="종료 단축키: Ctrl + Alt +", bg=BG, fg=TEXT, font=("Apple SD Gothic Neo", 13, "bold")).pack(side="left")

        quit_hotkey_entry = tk.Entry(
            quit_hotkey_frame, textvariable=tmp_quit_hotkey, width=3, justify="center",
            font=("Apple SD Gothic Neo", 13, "bold"), bg=CARD, fg=TEXT,
            insertbackground=TEXT, relief="flat", validate="key", validatecommand=vcmd,
        )
        quit_hotkey_entry.pack(side="left", padx=(8, 0))

        conflict_label = tk.Label(inner, text="", bg=BG, fg=RED, font=("Apple SD Gothic Neo", 11, "bold"))
        conflict_label.pack(anchor="w", padx=28, pady=(4, 0))

        def _check_hotkey_conflict(*_):
            a = tmp_hotkey.get().strip().lower()
            b = tmp_quit_hotkey.get().strip().lower()
            if a and b and a == b:
                conflict_label.config(text="⚠ 창 토글 단축키와 종료 단축키가 같아요.⚠")
            else:
                conflict_label.config(text="")

        tmp_hotkey.trace_add("write", _check_hotkey_conflict)
        tmp_quit_hotkey.trace_add("write", _check_hotkey_conflict)

        # --- 알림 설정 ---
        tk.Label(inner, text="알림", font=("Apple SD Gothic Neo", 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=28, pady=(22, 4))
        tk.Label(inner, text="기준값을 넘으면 윈도우 알림(토스트)으로 알려줍니다.", font=("Apple SD Gothic Neo", 11, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=28, pady=(0, 6))
        ttk.Checkbutton(inner, text="임계값 알림 사용", variable=tmp_alert, style="Dark.TCheckbutton").pack(anchor="w", padx=30)

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

            new_hotkey      = tmp_hotkey.get().strip() or app.hotkey_key.get()
            new_quit_hotkey = tmp_quit_hotkey.get().strip() or app.quit_hotkey_key.get()
            if new_hotkey.lower() == new_quit_hotkey.lower():
                # 두 단축키가 같아지면 둘 다 변경하지 않고 기존 값 유지
                new_hotkey      = app.hotkey_key.get()
                new_quit_hotkey = app.quit_hotkey_key.get()

            hotkey_changed = new_hotkey != app.hotkey_key.get()
            app.hotkey_key.set(new_hotkey)

            quit_hotkey_changed = new_quit_hotkey != app.quit_hotkey_key.get()
            app.quit_hotkey_key.set(new_quit_hotkey)

            if hotkey_changed:
                app.register_hotkey()
            if quit_hotkey_changed:
                app.register_quit_hotkey()

            app.alert_enabled.set(tmp_alert.get())

            save_settings({
                **{k: v.get() for k, v in app.show_vars.items()},
                "cpu_hot":          app.cpu_hot.get(),
                "ram_hot":          app.ram_hot.get(),
                "battery_low":      app.battery_low.get(),
                "disk_hot":         app.disk_hot.get(),
                "refresh_interval": app.refresh_interval.get(),
                "auto_refresh":     app.auto_refresh.get(),
                "hotkey_key":       app.hotkey_key.get(),
                "quit_hotkey_key":  app.quit_hotkey_key.get(),
                "alert_enabled":    app.alert_enabled.get(),
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
