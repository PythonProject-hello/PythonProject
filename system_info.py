"""
시스템 정보 수집 모듈
애들이 이 함수들의 구현을 수정/추가하면 됩니다.
"""

import os
import re
import shutil
import socket
import subprocess


def run_cmd(cmd):
    """셸 명령어 실행 및 결과 반환"""
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def get_cpu():
    """CPU 사용률 반환 (0.0 ~ 100.0)"""
    raw = run_cmd("ps -A -o %cpu | awk 'NR>1 {s+=$1} END {print s}'")
    try:
        return round(min(float(raw) / max(os.cpu_count() or 1, 1), 100), 1)
    except Exception:
        return 0.0


def get_ram():
    """메모리 사용률 반환 (percent, "사용GB / 전체GB")"""
    output = run_cmd("vm_stat")
    pages = {}
    for line in output.splitlines():
        match = re.match(r"(.+):\s+([0-9]+)\.", line.strip())
        if match:
            pages[match.group(1)] = int(match.group(2))

    page_size = 16384
    free = pages.get("Pages free", 0) + pages.get("Pages speculative", 0)
    used = (
        pages.get("Pages active", 0)
        + pages.get("Pages inactive", 0)
        + pages.get("Pages wired down", 0)
        + pages.get("Pages occupied by compressor", 0)
    )
    total = max(used + free, 1)
    used_gb = used * page_size / (1024 ** 3)
    total_gb = total * page_size / (1024 ** 3)
    return round(used / total * 100, 1), f"{used_gb:.1f}GB / {total_gb:.1f}GB"


def get_disk():
    """디스크 사용률 반환 (percent, "사용GB / 전체GB")"""
    usage = shutil.disk_usage("/")
    return (
        round(usage.used / usage.total * 100, 1),
        f"{usage.used / (1024 ** 3):.1f}GB / {usage.total / (1024 ** 3):.1f}GB",
    )


def get_battery():
    """배터리 수준 및 상태 반환 (percent, "전원 연결"/"배터리")"""
    output = run_cmd("pmset -g batt")
    match = re.search(r"(\d+)%", output)
    value = float(match.group(1)) if match else 0.0
    source = "전원 연결" if "AC Power" in output else "배터리"
    return round(value, 1), source


def get_network():
    """네트워크 IP 주소 반환"""
    ip = run_cmd("ipconfig getifaddr en0")
    if ip:
        return ip
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "확인 안 됨"
