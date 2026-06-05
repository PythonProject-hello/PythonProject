import os
import time
import tkinter as tk
from tkinter import ttk

from system_info import get_cpu, get_ram, get_disk, get_battery, get_network


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

APP_W = 1240
APP_H = 800

BG = "#0f1115"
PANEL = "#1a1f27"
CARD = "#252b35"
LINE = "#3a4350"
TEXT = "#f4f2ee"
MUTED = "#9da5b1"
BLUE = "#62a8ff"
GREEN = "#7dd87d"
YELLOW = "#ffd166"
RED = "#ff6b6b"
PURPLE = "#b98cff"

MOOD_FILES = {
    "hard_work": "mood1.png",
    "hungry": "mood2.png",
    "sad": "mood3.png",
    "calm": "mood4.png",
    "good": "mood5.png",
    "full": "mood6.png",
    "peaceful": "mood7.png",
}


def rounded_rect(canvas, x1, y1, x2, y2, radius=22, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def safe_load_image(root, path, max_w=300, max_h=260, fill="#fffaf2"):
    """이미지를 안전하게 로드하고 최대 크기에 맞게 리사이즈합니다.

    - Pillow(PIL)가 설치되어 있으면 이를 사용해 고품질로 리사이즈합니다.
    - 없으면 `tk.PhotoImage`로 로드한 뒤 `subsample`으로 단계적으로 축소합니다.
    - 파일이 없거나 로드 실패 시 플레이스홀더 이미지를 반환합니다.
    """
    # Pillow 경로 (우선 시도)
    try:
        from PIL import Image, ImageTk
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            # 작은 더미(예: 1x1) 파일인 경우 플레이스홀더로 처리
            if img.size[0] < 50 or img.size[1] < 50:
                raise Exception("image too small")
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            return ImageTk.PhotoImage(img, master=root)
    except Exception:
        pass

    # Tk 기반 축소(대체 경로)
    try:
        if os.path.exists(path):
            img = tk.PhotoImage(master=root, file=path)
            w, h = img.width(), img.height()
            # 1x1 등 작은 더미 이미지는 무시
            if w < 50 or h < 50:
                raise Exception("image too small")
            # 간단한 반복 subsample로 크기 줄이기 (2배씩)
            while (w > max_w or h > max_h):
                img = img.subsample(2, 2)
                w, h = img.width(), img.height()
            return img
    except Exception:
        pass

    # 플레이스홀더
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

        self.show_vars = {
            "cpu": tk.BooleanVar(value=True),
            "ram": tk.BooleanVar(value=True),
            "disk": tk.BooleanVar(value=True),
            "battery": tk.BooleanVar(value=True),
            "network": tk.BooleanVar(value=False),
        }
        self.cpu_hot = tk.IntVar(value=75)
        self.ram_hot = tk.IntVar(value=82)
        self.battery_low = tk.IntVar(value=25)
        self.auto_refresh = tk.BooleanVar(value=False)
        self.auto_job = None

        self.data = {}
        # 이미지가 없을 때도 앱이 실행되도록 안전하게 로드
        self.images = {
            key: safe_load_image(self.root, os.path.join(ASSET_DIR, filename))
            for key, filename in MOOD_FILES.items()
        }

        self.canvas = tk.Canvas(self.root, width=APP_W, height=APP_H, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.canvas.tag_bind("refresh_btn", "<Button-1>", lambda _event: self.refresh())
        self.canvas.tag_bind("settings_btn", "<Button-1>", lambda _event: self.open_settings())
        self.refresh()

    def refresh(self):
        self.data = {
            "cpu": get_cpu(),
            "ram": get_ram(),
            "disk": get_disk(),
            "battery": get_battery(),
            "network": get_network(),
            "time": time.strftime("%H:%M:%S"),
        }
        self.draw()

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("설정")
        win.geometry("430x540")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(
            win,
            text="컴퓨팅 자원 설정",
            font=("Apple SD Gothic Neo", 25, "bold"),
            bg=BG,
            fg=TEXT,
        ).pack(anchor="w", padx=28, pady=(26, 6))

        tk.Label(
            win,
            text="표시할 정보와 캐릭터 반응 기준을 조절합니다.",
            font=("Apple SD Gothic Neo", 13, "bold"),
            bg=BG,
            fg=MUTED,
        ).pack(anchor="w", padx=28, pady=(0, 18))

        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure("Dark.TCheckbutton", background=PANEL, foreground=TEXT, font=("Apple SD Gothic Neo", 15, "bold"))
        style.map("Dark.TCheckbutton", background=[("active", PANEL)], foreground=[("active", TEXT)])

        box = tk.Frame(win, bg=PANEL, padx=18, pady=14)
        box.pack(fill="x", padx=26, pady=(0, 16))
        for key, text in [
            ("cpu", "CPU 사용률"),
            ("ram", "메모리 사용량"),
            ("disk", "저장 공간"),
            ("battery", "배터리"),
            ("network", "네트워크 IP"),
        ]:
            ttk.Checkbutton(box, text=text, variable=self.show_vars[key], command=self.draw, style="Dark.TCheckbutton").pack(anchor="w", pady=6)

        self.make_slider(win, "CPU 힘듦 기준", self.cpu_hot, 40, 95, "%")
        self.make_slider(win, "RAM 과부하 기준", self.ram_hot, 50, 95, "%")
        self.make_slider(win, "배터리 배고픔 기준", self.battery_low, 5, 60, "%")

        ttk.Checkbutton(
            win,
            text="5초마다 자동 새로고침",
            variable=self.auto_refresh,
            command=self.toggle_auto_refresh,
            style="Dark.TCheckbutton",
        ).pack(anchor="w", padx=30, pady=(8, 0))

        tk.Button(
            win,
            text="완료",
            command=win.destroy,
            font=("Apple SD Gothic Neo", 15, "bold"),
            bg=BLUE,
            fg="#071018",
            bd=0,
            padx=28,
            pady=10,
            cursor="hand2",
        ).pack(anchor="e", padx=28, pady=22)

    def make_slider(self, parent, title, variable, start, end, suffix):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", padx=28, pady=7)
        label = tk.Label(frame, text=f"{title}: {variable.get()}{suffix}", bg=BG, fg=TEXT, font=("Apple SD Gothic Neo", 13, "bold"))
        label.pack(anchor="w")

        def changed(value):
            label.config(text=f"{title}: {int(float(value))}{suffix}")
            self.draw()

        tk.Scale(
            frame,
            from_=start,
            to=end,
            orient="horizontal",
            variable=variable,
            command=changed,
            bg=BG,
            fg=MUTED,
            troughcolor=CARD,
            highlightthickness=0,
            activebackground=BLUE,
        ).pack(fill="x")

    def toggle_auto_refresh(self):
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        if self.auto_refresh.get():
            self.schedule_refresh()

    def schedule_refresh(self):
        self.refresh()
        self.auto_job = self.root.after(5000, self.schedule_refresh)

    def mood(self):
        import random
        cpu = self.data.get("cpu", 0)
        ram = self.data.get("ram", (0, ""))[0]
        battery = self.data.get("battery", (100, ""))[0]

        # 과부하 모드: CPU나 RAM이 높음
        if cpu >= self.cpu_hot.get() or ram >= self.ram_hot.get():
            return "hard_work", "과부하 모드", "주인님, 힘들어요", RED, "HOT"
        
        # 배터리 부족
        if battery <= self.battery_low.get():
            return "hungry", "배터리 부족", "주인님, 배고파요", YELLOW, "LOW"
        
        # 배터리 충만 및 좋은 상태
        if battery >= 98:
            return "full", "배터리 만땅", "배불러요, 주인님", GREEN, "FULL"
        if battery >= 80 and cpu <= 30 and ram <= 70:
            return "good", "좋은 컨디션", "딱, 좋아요, 주인님", GREEN, "GOOD"
        
        # 유휴 상태: CPU와 RAM이 모두 낮음 → "어디있어요, 주인님" 중 랜덤 선택
        if cpu <= 12 and ram <= 60:
            mood_key = random.choice(["sad", "calm"])
            messages = {
                "sad": "너무 조용함",
                "calm": "조용한 상태"
            }
            return mood_key, messages[mood_key], "어디있어요, 주인님", BLUE, "IDLE"
        
        # 기본: 편안한 상태
        return "peaceful", "쾌적한 상태", "편안해요, 주인님", GREEN, "OK"

    def draw(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_header()
        self.draw_icon_button(1080, 54, "↻", "refresh_btn", BLUE, TEXT)
        self.draw_icon_button(1150, 54, "⚙", "settings_btn", CARD, TEXT)
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

    def draw_icon_button(self, x, y, icon, tag, fill, fg):
        self.canvas.create_text(x + 29, y + 29, text=icon, fill=fg, font=("Apple SD Gothic Neo", 30, "bold"), tags=tag)

    def draw_header(self):
        self.canvas.create_text(
            76,
            58,
            text="주인님, 확인해주세요!",
            anchor="nw",
            fill=TEXT,
            font=("Apple SD Gothic Neo", 28, "bold"),
        )
        self.canvas.create_text(
            78,
            100,
            text="CPU와 메모리 상태를 하치와레 멘트로 보여주는 미니 대시보드",
            anchor="nw",
            fill=MUTED,
            font=("Apple SD Gothic Neo", 13, "bold"),
        )
        self.canvas.create_text(
            1062,
            118,
            text=f"마지막 갱신 {self.data.get('time', '-')}",
            anchor="ne",
            fill="#7f8792",
            font=("Apple SD Gothic Neo", 12, "bold"),
        )

    def visible_metrics(self):
        # 고정: 요청대로 순서 및 라벨을 고정 표시합니다.
        # 순서: CPU, 메모리, 디스크, 배터리, 램
        items = []

        cpu = self.data.get("cpu", 0)
        items.append(("CPU", cpu, "프로세서 사용률", BLUE, f"{cpu:.1f}%"))

        mem = self.data.get("ram", (0, "-"))
        # '메모리' 항목
        items.append(("메모리", mem[0], f"메모리 사용량 · {mem[1]}", PURPLE, f"{mem[0]:.1f}%"))

        disk = self.data.get("disk", (0, "-"))
        items.append(("디스크", disk[0], disk[1], GREEN, f"{disk[0]:.1f}%"))

        batt = self.data.get("battery", (0, "-"))
        items.append(("배터리", batt[0], batt[1], YELLOW, f"{batt[0]:.1f}%"))

        # 추가로 '램' 항목(요청 반영) - 같은 메모리 수치 사용
        items.append(("램", mem[0], f"램 사용량 · {mem[1]}", PURPLE, f"{mem[0]:.1f}%"))

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
        row_spacing = 14
        for item in items:
            self.draw_metric(x + 30, row_y, w - 60, row_h, *item)
            row_y += row_h + row_spacing

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
        self.canvas.create_text(
            msg_x + 30,
            msg_y + 28,
            text=message,
            anchor="nw",
            fill=color,
            font=("Apple SD Gothic Neo", 24, "bold"),
            width=w - 128,
        )

        box_x, box_y = x + 84, y + 284
        box_w, box_h = 350, 280
        # 배경 박스 제거 - 이미지만 표시하고 배경은 그리지 않음
        # rounded_rect(self.canvas, box_x, box_y, box_x + box_w, box_y + box_h, 34, fill="#fffaf2", outline="#303640", width=2)
        # 이미지가 박스 내부에 잘 맞도록 필요시 리사이즈 후 중앙에 배치
        img = self.images.get(key)
        if img:
            try:
                w = img.width()
                h = img.height()
            except Exception:
                # PhotoImage가 아닌 경우 무시
                w = h = 0

            max_w = box_w - 40
            max_h = box_h - 40
            if w == 0 or h == 0 or w > max_w or h > max_h:
                # 원본 파일을 재로드하여 박스 크기에 맞게 리사이즈
                filename = MOOD_FILES.get(key, f"{key}.png")
                path = os.path.join(ASSET_DIR, filename)
                new_img = safe_load_image(self.root, path, max_w=max_w, max_h=max_h)
                # 캐시 교체
                self.images[key] = new_img
                img = new_img

        # 이미지가 박스 상단에 정렬되도록 표시 (항상 위쪽 여백 유지)
        try:
            iw, ih = img.width(), img.height()
        except Exception:
            iw = ih = 0

        if iw and ih:
            top_padding = 10
            # 상단 정렬: 이미지의 상단(y)을 box_y + top_padding로 고정 (anchor='n')
            target_x = box_x + box_w / 2
            target_y = box_y + top_padding
            # 만약 이미지가 박스 하단을 침범하면 중앙으로 안전하게 이동
            if target_y + ih > box_y + box_h - 12:
                # 중앙 배치
                self.canvas.create_image(box_x + box_w / 2, box_y + box_h / 2, image=img, anchor="center")
            else:
                self.canvas.create_image(target_x, target_y, image=img, anchor="n")
        else:
            self.canvas.create_image(box_x + box_w / 2, box_y + box_h / 2, image=img, anchor="center")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    StatusApp().run()
