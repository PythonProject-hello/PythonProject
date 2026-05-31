# 캐릭터 반응 기준값
MOOD_THRESHOLDS = {
    "tired_cpu":    50,
    "tired_memory": 60,
    "panic_cpu":    80,
    "panic_memory": 85,
    "low_battery":  50,
    "tired_disk":   40,
}

# 모니터링 갱신 주기 (초)
REFRESH_INTERVAL = 2

# 자원 표시 설정 (키, 라벨, 기본 On/Off, 포맷)
# 포맷: "bool" → 충전중/미충전, 그 외 → format() 문자열
RESOURCES = [
    ("cpu",               "CPU 사용률",        True,  "{:.1f}%"),
    ("cpu_freq",          "CPU 클럭",   False, "{:.2f} GHz"),
    ("memory",            "RAM 사용률",        True,  "{:.1f}%"),
    ("memory_used_gb",    "RAM 사용량", False, "{:.1f} GB"),
    ("memory_total_gb",   "RAM 전체 용량",   False, "{:.1f} GB"),
    ("memory_available_gb","RAM 여유 용량",  False, "{:.1f} GB"),
    ("disk",              "디스크 사용률",     False, "{:.1f}%"),
    ("battery",           "배터리 잔량",     False, "{:.1f}%"),
    ("charging",          "충전 여부",  False, "bool"),
]

# 메인 화면에 슬라이더(프로그레스바)로 표시할 자원 기본값
# % 단위 자원만 해당 (GHz, GB, bool 제외)
SLIDER_DEFAULTS = {
    "cpu":     True,
    "memory":  True,
    "disk":    False,
    "battery": False,
}
