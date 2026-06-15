import os
import sys
import json
import time
import subprocess
import tkinter as tk

try:
    import keyboard
except Exception:
    keyboard = None

if sys.platform == "win32":
    from winotify import Notification
else:
    Notification = None

from core.monitor import project_data, get_top_processes
from core.character import get_dialogue
from config.settings import (
    DEFAULT_RESOURCES,
    MIN_REFRESH_INTERVAL,
    MAX_REFRESH_INTERVAL,
    MIN_PROCESS_INTERVAL,
    MAX_PROCESS_INTERVAL,
    DEFAULT_THRESHOLDS,
    DEFAULT_HOTKEY_KEY,
    DEFAULT_ALERT_ENABLED,
    load_settings,
)

ALERT_HOLD_SECONDS = 5
ALERT_POLL_SECONDS = 1

ALERTS = [
    # (show_vars 키, raw 데이터 키, 임계값 키, 비교 방식, 알림 제목, 알림 메시지)
    ("cpu",     "cpu",     "cpu_hot",     "ge", "CPU 사용률",   "CPU 사용률이 {value:.0f}%로 기준({thresh}%)을 넘었어요."),
    ("ram",     "memory",  "ram_hot",     "ge", "메모리 사용량", "메모리 사용량이 {value:.0f}%로 기준({thresh}%)을 넘었어요."),
    ("disk",    "disk",    "disk_hot",    "ge", "저장 공간",    "디스크 사용량이 {value:.0f}%로 기준({thresh}%)을 넘었어요."),
    ("battery", "battery", "battery_low", "le", "배터리",      "배터리가 {value:.0f}%로 기준({thresh}%) 이하예요."),
]

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

APP_W = 1240
APP_H = 800

BG     = "#0f1115"
PANEL  = "#1a1f27"
CARD   = "#252b35"
LINE   = "#3a4350"
TEXT   = "#f4f2ee"
MUTED  = "#9da5b1"
BLUE   = "#62a8ff"
GREEN  = "#7dd87d"
YELLOW = "#ffd166"
RED    = "#ff6b6b"
PURPLE = "#b98cff"

MOOD_FILES = {
    "hard_work": "mood1.png",
    "hungry":    "mood2.png",
    "sad":       "mood3.png",
    "calm":      "mood4.png",
    "good":      "mood5.png",
    "full":      "mood6.png",
    "peaceful":  "mood7.png",
}


def rounded_rect(canvas, x1, y1, x2, y2, radius=22, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def safe_load_image(root, path, max_w=300, max_h=260, fill="#fffaf2"):
    try:
        from PIL import Image, ImageTk
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            if img.size[0] < 50 or img.size[1] < 50:
                raise Exception("image too small")
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            return ImageTk.PhotoImage(img, master=root)
    except Exception:
        pass

    try:
        if os.path.exists(path):
            img = tk.PhotoImage(master=root, file=path)
            w, h = img.width(), img.height()
            if w < 50 or h < 50:
                raise Exception("image too small")
            while w > max_w or h > max_h:
                img = img.subsample(2, 2)
                w, h = img.width(), img.height()
            return img
    except Exception:
        pass

    try:
        img = tk.PhotoImage(master=root, width=max_w, height=max_h)
        img.put((fill,), to=(0, 0, max_w - 1, max_h - 1))
        return img
    except Exception:
        return tk.PhotoImage(master=root)


class StatusApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("주인님 확인해주세요")
        self.root.geometry(f"{APP_W}x{APP_H}")
        self.root.minsize(APP_W, APP_H)
        self.root.maxsize(APP_W, APP_H)
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        _saved = load_settings()

        self.show_vars = {
            key: tk.BooleanVar(value=_saved.get(key, default))
            for key, default in DEFAULT_RESOURCES.items()
        }

        def _t(key): return _saved.get(key, DEFAULT_THRESHOLDS[key])
        self.cpu_hot          = tk.IntVar(value=_t("cpu_hot"))
        self.ram_hot          = tk.IntVar(value=_t("ram_hot"))
        self.battery_low      = tk.IntVar(value=_t("battery_low"))
        self.disk_hot         = tk.IntVar(value=_t("disk_hot"))
        self.refresh_interval = tk.IntVar(value=_t("refresh_interval"))
        self.process_interval      = tk.IntVar(value=_t("process_interval"))
        self.process_cpu_threshold = tk.IntVar(value=_t("process_cpu_threshold"))
        self.process_mem_threshold = tk.IntVar(value=_t("process_mem_threshold"))
        self.auto_refresh     = tk.BooleanVar(value=_saved.get("auto_refresh", True))
        self.process_auto     = tk.BooleanVar(value=_saved.get("process_auto", True))
        self.hotkey_key       = tk.StringVar(value=_saved.get("hotkey_key", DEFAULT_HOTKEY_KEY))
        self.alert_enabled    = tk.BooleanVar(value=_saved.get("alert_enabled", DEFAULT_ALERT_ENABLED))
        self.auto_job = None
        self.process_job = None
        self.settings_win = None
        self.hotkey_handle = None
        self._alert_active = set()
        self._alert_pending = {}
        self.alert_job = None

        self.data   = {}
        self.process_data = []
        self.images = {
            key: safe_load_image(self.root, os.path.join(ASSET_DIR, filename))
            for key, filename in MOOD_FILES.items()
        }

        self.canvas = tk.Canvas(self.root, width=APP_W, height=APP_H, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.canvas.tag_bind("refresh_btn",  "<Button-1>", lambda _: self.refresh())
        self.canvas.tag_bind("settings_btn", "<Button-1>", lambda _: self.open_settings())
        self.refresh()
        self.toggle_auto_refresh()
        self.toggle_process_auto()
        self.register_hotkey()

    def refresh(self):
        active = {key for key, var in self.show_vars.items() if var.get()}
        raw    = project_data()

        self.data = {"time": time.strftime("%H:%M:%S"), "_raw": raw}

        if "cpu" in active:
            self.data["cpu"] = raw["cpu"]
        if "ram" in active:
            self.data["ram"] = (raw["memory"], f"{raw['memory_used_gb']}GB / {raw['memory_total_gb']}GB")
        if "disk" in active:
            self.data["disk"] = (raw["disk"], f"{raw['disk_used_gb']}GB / {raw['disk_total_gb']}GB")
        if "battery" in active:
            bat_pct   = raw["battery"] if raw["battery"] is not None else 0
            bat_label = "전원 연결" if raw["charging"] else "배터리"
            self.data["battery"] = (bat_pct, bat_label)

        self.check_alerts(raw, active)
        if self.root.state() != "withdrawn":
            self.draw()

    def check_alerts(self, raw, active):
        if not self.alert_enabled.get() or self.root.state() != "withdrawn":
            self._cancel_alert_poll()
            self._alert_pending.clear()
            return

        thresholds = {
            "cpu_hot":     self.cpu_hot.get(),
            "ram_hot":     self.ram_hot.get(),
            "disk_hot":    self.disk_hot.get(),
            "battery_low": self.battery_low.get(),
        }

        any_pending = False
        for show_key, raw_key, thresh_key, cmp, label, msg_fmt in ALERTS:
            if show_key not in active:
                continue
            key    = raw_key
            value  = raw.get(raw_key)
            thresh = thresholds[thresh_key]
            if value is None:
                continue

            triggered = value >= thresh if cmp == "ge" else value <= thresh
            if not triggered:
                self._alert_pending.pop(key, None)
                self._alert_active.discard(key)
                continue

            if key in self._alert_active:
                continue

            first_seen = self._alert_pending.setdefault(key, time.time())
            if time.time() - first_seen >= ALERT_HOLD_SECONDS:
                self._alert_active.add(key)
                self._alert_pending.pop(key, None)
                self.notify(label, msg_fmt.format(value=value, thresh=thresh))
            else:
                any_pending = True

        if any_pending:
            self._ensure_alert_poll()
        else:
            self._cancel_alert_poll()

    def _ensure_alert_poll(self):
        if self.alert_job is None:
            self.alert_job = self.root.after(ALERT_POLL_SECONDS * 1000, self._poll_alerts)

    def _cancel_alert_poll(self):
        if self.alert_job is not None:
            self.root.after_cancel(self.alert_job)
            self.alert_job = None

    def _poll_alerts(self):
        self.alert_job = None
        active = {key for key, var in self.show_vars.items() if var.get()}
        self.check_alerts(project_data(), active)

    def notify(self, title, message):
        try:
            if sys.platform == "win32":
                Notification(
                    app_id="주인님 확인해주세요",
                    title=title,
                    msg=message,
                ).show()
            elif sys.platform == "darwin":
                script = f"display notification {json.dumps(message)} with title {json.dumps(title)}"
                subprocess.run(["osascript", "-e", script], check=False)
        except Exception:
            pass

    def open_settings(self):
        if self.settings_win is not None and self.settings_win.winfo_exists():
            self.settings_win.destroy()
            self.settings_win = None
            return

        from ui.settings_window import SettingsWindow
        self.settings_win = SettingsWindow(self).win

    def toggle_auto_refresh(self):
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        if self.auto_refresh.get():
            self._schedule_next_refresh()

    def _schedule_next_refresh(self):
        interval_ms = max(MIN_REFRESH_INTERVAL, min(MAX_REFRESH_INTERVAL, self.refresh_interval.get())) * 1000
        self.auto_job = self.root.after(interval_ms, self.schedule_refresh)

    def schedule_refresh(self):
        self.refresh()
        self._schedule_next_refresh()

    def check_processes(self):
        self.process_data = get_top_processes(
            cpu_threshold=self.process_cpu_threshold.get(),
            mem_threshold=self.process_mem_threshold.get(),
        )

    def schedule_process_check(self):
        self.check_processes()
        interval_ms = max(MIN_PROCESS_INTERVAL, min(MAX_PROCESS_INTERVAL, self.process_interval.get())) * 60 * 1000
        self.process_job = self.root.after(interval_ms, self.schedule_process_check)

    def toggle_process_auto(self):
        if self.process_job:
            self.root.after_cancel(self.process_job)
            self.process_job = None
        if self.process_auto.get():
            self.schedule_process_check()

    def register_hotkey(self):
        if keyboard is None:
            return

        if self.hotkey_handle is not None:
            keyboard.remove_hotkey(self.hotkey_handle)
            self.hotkey_handle = None

        combo = f"ctrl+alt+{self.hotkey_key.get().lower()}"
        try:
            self.hotkey_handle = keyboard.add_hotkey(
                combo, lambda: self.root.after(0, self.toggle_window)
            )
        except Exception:
            self.hotkey_handle = None

    def toggle_window(self):
        has_settings = self.settings_win is not None and self.settings_win.winfo_exists()
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            if has_settings:
                self.settings_win.deiconify()
                self.settings_win.lift()
            self.refresh()
        else:
            if has_settings:
                self.settings_win.withdraw()
            self.root.withdraw()

    def mood(self):
        import random
        # 모니터링하지 않는 자원은 기분 판정에서 제외 (CPU/RAM 0%, 배터리 100% 취급)
        cpu     = self.data.get("cpu", 0)
        ram     = self.data.get("ram", (0, ""))[0]
        battery = self.data.get("battery", (100, ""))[0]
        raw     = self.data.get("_raw", {})

        thresholds = {
            "tired_cpu":    self.cpu_hot.get(),
            "tired_memory": self.ram_hot.get(),
            "low_battery":  self.battery_low.get(),
            "tired_disk":   self.disk_hot.get(),
        }
        dialogue = get_dialogue(raw, thresholds)

        if cpu >= self.cpu_hot.get() or ram >= self.ram_hot.get():
            return "hard_work", "과부하 모드", dialogue, RED, "HOT"
        if battery <= self.battery_low.get():
            return "hungry", "배터리 부족", dialogue, YELLOW, "LOW"
        if battery >= 98:
            return "full", "배터리 만땅", dialogue, GREEN, "FULL"
        if battery >= 80 and cpu <= 30 and ram <= 70:
            return "good", "좋은 컨디션", dialogue, GREEN, "GOOD"
        if cpu <= 12 and ram <= 60:
            mood_key = random.choice(["sad", "calm"])
            messages = {"sad": "너무 조용함", "calm": "조용한 상태"}
            return mood_key, messages[mood_key], dialogue, BLUE, "IDLE"
        return "peaceful", "쾌적한 상태", dialogue, GREEN, "OK"

    def draw(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_header()
        self.draw_icon_button(1080, 54, "↻", "refresh_btn",  TEXT)
        self.draw_icon_button(1150, 54, "⚙", "settings_btn", TEXT)
        self.draw_status_panel()
        self.draw_character_panel()

    def draw_background(self):
        self.canvas.create_rectangle(0, 0, APP_W, APP_H, fill=BG, outline="")
        self.canvas.create_oval(-170, -230, 390, 330, fill="#142033", outline="")
        self.canvas.create_oval(900, 560, 1320, 960, fill="#1e3126", outline="")
        for x in range(64, APP_W, 86):
            self.canvas.create_line(x, 0, x, APP_H, fill="#161a1e")
        for y in range(64, APP_H, 86):
            self.canvas.create_line(0, y, APP_W, y, fill="#161a1e")

    def draw_icon_button(self, x, y, icon, tag, fg):
        self.canvas.create_text(x + 29, y + 29, text=icon, fill=fg, font=("Apple SD Gothic Neo", 30, "bold"), tags=tag)

    def draw_header(self):
        self.canvas.create_text(76, 58, text="주인님, 확인해주세요!", anchor="nw", fill=TEXT, font=("Apple SD Gothic Neo", 28, "bold"))
        self.canvas.create_text(78, 100, text="CPU와 메모리 상태를 하치와레 멘트로 보여주는 미니 대시보드", anchor="nw", fill=MUTED, font=("Apple SD Gothic Neo", 13, "bold"))
        self.canvas.create_text(1062, 118, text=f"마지막 갱신 {self.data.get('time', '-')}", anchor="ne", fill="#7f8792", font=("Apple SD Gothic Neo", 12, "bold"))

    def visible_metrics(self):
        items = []

        if self.show_vars["cpu"].get():
            cpu = self.data.get("cpu", 0)
            items.append(("CPU", cpu, "프로세서 사용률", BLUE, f"{cpu:.1f}%"))

        if self.show_vars["ram"].get():
            mem = self.data.get("ram", (0, "-"))
            items.append(("메모리", mem[0], f"메모리 사용량 · {mem[1]}", PURPLE, f"{mem[0]:.1f}%"))

        if self.show_vars["disk"].get():
            disk = self.data.get("disk", (0, "-"))
            items.append(("디스크", disk[0], disk[1], GREEN, f"{disk[0]:.1f}%"))

        if self.show_vars["battery"].get():
            batt = self.data.get("battery", (0, "-"))
            items.append(("배터리", batt[0], batt[1], YELLOW, f"{batt[0]:.1f}%"))

        return items

    def draw_status_panel(self):
        x, y, w, h = 76, 176, 510, 560
        rounded_rect(self.canvas, x, y, x + w, y + h, 38, fill=PANEL, outline=LINE, width=2)
        self.canvas.create_text(x + 34, y + 34, text="SYSTEM BOARD", anchor="nw", fill=MUTED, font=("Apple SD Gothic Neo", 12, "bold"))
        self.canvas.create_text(x + 34, y + 64, text="컴퓨터 상태 확인", anchor="nw", fill=TEXT, font=("Apple SD Gothic Neo", 22, "bold"))

        items = self.visible_metrics()
        if not items:
            self.canvas.create_text(x + 34, y + 130, text="⚙ 설정에서 표시할 자원을 켜주세요.", anchor="nw", fill=MUTED, font=("Apple SD Gothic Neo", 17, "bold"))
            return

        row_y = y + 130
        row_h = 68 if len(items) >= 5 else 88
        for item in items:
            self.draw_metric(x + 30, row_y, w - 60, row_h, *item)
            row_y += row_h + 14

    def draw_metric(self, x, y, w, h, name, value, sub, color, display_value):
        rounded_rect(self.canvas, x, y, x + w, y + h, 26, fill=CARD, outline="#303741")
        self.canvas.create_text(x + 24, y + 10, text=name, anchor="nw", fill=MUTED, font=("Apple SD Gothic Neo", 12, "bold"))
        self.canvas.create_text(x + w - 24, y + 8, text=display_value, anchor="ne", fill=TEXT, font=("Apple SD Gothic Neo", 18, "bold"))
        self.canvas.create_text(x + 24, y + 30, text=sub, anchor="nw", fill="#b6bdc7", font=("Apple SD Gothic Neo", 10, "bold"), width=w - 54)
        bar_y = y + h - 13
        bar_x = x + 24
        bar_w = w - 48
        self.canvas.create_line(bar_x, bar_y, bar_x + bar_w, bar_y, fill="#3a414b", width=7)
        self.canvas.create_line(bar_x, bar_y, bar_x + bar_w * min(value, 100) / 100, bar_y, fill=color, width=7)

    def draw_character_panel(self):
        key, title, message, color, badge = self.mood()
        x, y, w, h = 646, 176, 518, 560
        rounded_rect(self.canvas, x, y, x + w, y + h, 38, fill="#171a1e", outline=color, width=2)
        self.canvas.create_text(x + 34, y + 34, text="HACHIWARE STATUS", anchor="nw", fill=color, font=("Apple SD Gothic Neo", 12, "bold"))
        self.canvas.create_text(x + 34, y + 68, text=title, anchor="nw", fill=TEXT, font=("Apple SD Gothic Neo", 26, "bold"))

        rounded_rect(self.canvas, x + w - 140, y + 34, x + w - 34, y + 66, 17, fill=color, outline="")
        self.canvas.create_text(x + w - 87, y + 50, text=badge, fill="#101214", font=("Apple SD Gothic Neo", 13, "bold"))

        msg_x, msg_y = x + 40, y + 136
        rounded_rect(self.canvas, msg_x, msg_y, x + w - 40, msg_y + 96, 30, fill=CARD, outline="#303741")
        self.canvas.create_text(msg_x + 30, msg_y + 28, text=message, anchor="nw", fill=color, font=("Apple SD Gothic Neo", 24, "bold"), width=w - 128)

        box_x, box_y = x + 84, y + 284
        box_w, box_h = 350, 280
        img = self.images.get(key)
        if img:
            try:
                iw, ih = img.width(), img.height()
            except Exception:
                iw = ih = 0

            max_w = box_w - 40
            max_h = box_h - 40
            if iw == 0 or ih == 0 or iw > max_w or ih > max_h:
                filename = MOOD_FILES.get(key, f"{key}.png")
                path     = os.path.join(ASSET_DIR, filename)
                new_img  = safe_load_image(self.root, path, max_w=max_w, max_h=max_h)
                self.images[key] = new_img
                img = new_img

        try:
            iw, ih = img.width(), img.height()
        except Exception:
            iw = ih = 0

        if iw and ih:
            target_x = box_x + box_w / 2
            target_y = box_y + 10
            if target_y + ih > box_y + box_h - 12:
                self.canvas.create_image(box_x + box_w / 2, box_y + box_h / 2, image=img, anchor="center")
            else:
                self.canvas.create_image(target_x, target_y, image=img, anchor="n")
        else:
            self.canvas.create_image(box_x + box_w / 2, box_y + box_h / 2, image=img, anchor="center")

    def run(self):
        self.root.mainloop()
