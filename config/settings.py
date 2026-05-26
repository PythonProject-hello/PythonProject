# 캐릭터 반응 기준값
MOOD_THRESHOLDS = {
    "tired_cpu": 50,
    "tired_ram": 60,
    "panic_cpu": 80,
    "panic_ram": 85,
}

# 모니터링 갱신 주기 (초)
REFRESH_INTERVAL = 2

# 자원 표시 설정 (키, 라벨, 기본 On/Off, 포맷)
# 포맷: "bool" → 충전중/미충전, 그 외 → format() 문자열
RESOURCES = [
    ("cpu",              "CPU",        True,  "{:.1f}%"),
    ("cpu_freq",         "CPU 클럭",   False, "{:.2f} GHz"),
    ("ram",              "RAM",        True,  "{:.1f}%"),
    ("ram_used_gb",      "RAM 사용량", False, "{:.1f} GB"),
    ("ram_total_gb",     "RAM 전체",   False, "{:.1f} GB"),
    ("ram_available_gb", "RAM 여유",   False, "{:.1f} GB"),
    ("disk",             "디스크",     False, "{:.1f}%"),
    ("network",          "네트워크",   False, "{:.1f} KB/s"),
    ("battery",          "배터리",     False, "{:.1f}%"),
    ("charging",         "충전 상태",  False, "bool"),
]

# 메인 화면에 슬라이더(프로그레스바)로 표시할 자원 기본값
# % 단위 자원만 해당 (GHz, GB, bool 제외)
SLIDER_DEFAULTS = {
    "cpu":     True,
    "ram":     True,
    "disk":    False,
    "battery": False,
}
