import os
import json

# 기본으로 모니터링(표시 + 수집)할 자원
DEFAULT_RESOURCES = {
    "cpu":     True,
    "ram":     True,
    "disk":    True,
    "battery": True,
}

# 갱신 주기 기본값 (초). 슬라이더 범위: 1~10
DEFAULT_REFRESH_INTERVAL = 5
MIN_REFRESH_INTERVAL = 1
MAX_REFRESH_INTERVAL = 10

# 프로세스 측정 주기 기본값 (분). 슬라이더 범위: 1~10
DEFAULT_PROCESS_INTERVAL = 5
MIN_PROCESS_INTERVAL = 1
MAX_PROCESS_INTERVAL = 10

# 반응 기준값 기본값
DEFAULT_THRESHOLDS = {
    "cpu_hot":              75,
    "ram_hot":              82,
    "battery_low":          25,
    "disk_hot":             40,
    "refresh_interval":     DEFAULT_REFRESH_INTERVAL,
    "process_interval":     DEFAULT_PROCESS_INTERVAL,
    "process_cpu_threshold": 10,
    "process_mem_threshold": 10,
}

# 창 보이기/숨기기 단축키 (Ctrl+Alt+<키>). <키>만 변경 가능
DEFAULT_HOTKEY_KEY = "m"

# 프로그램 종료 단축키 (Ctrl+Alt+<키>). <키>만 변경 가능
DEFAULT_QUIT_HOTKEY_KEY = "q"

# 임계값 초과 시 토스트 알림 기본 사용 여부
DEFAULT_ALERT_ENABLED = True

# 프리셋
PRESETS = {
    "안 표독": {"cpu_hot": 90, "ram_hot": 90, "battery_low": 15, "disk_hot": 80},
    "덜 표독":       {"cpu_hot": 75, "ram_hot": 82, "battery_low": 25, "disk_hot": 40},
    "표독":       {"cpu_hot": 55, "ram_hot": 65, "battery_low": 40, "disk_hot": 20},
}

_SAVE_PATH = os.path.join(os.getenv("APPDATA", "."), "Pyject", "settings.json")


def load_settings() -> dict:
    try:
        with open(_SAVE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data: dict):
    os.makedirs(os.path.dirname(_SAVE_PATH), exist_ok=True)
    with open(_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
