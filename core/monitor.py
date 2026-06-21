import os
import psutil

# cpu_percent(interval=None)은 직전 호출 이후 사용률을 즉시 반환(논블로킹)하므로
# 최초 기준점을 만들어 둬야 첫 측정값이 0.0으로 나오지 않음
psutil.cpu_percent(interval=None)


def project_data():
    data = {}

    data["cpu"] = psutil.cpu_percent(interval=None)

    mem = psutil.virtual_memory()
    data["memory"]          = mem.percent
    data["memory_used_gb"]  = round(mem.used / 1e9, 1)
    data["memory_total_gb"] = round(mem.total / 1e9, 1)

    bat = psutil.sensors_battery()
    data["battery"]  = bat.percent       if bat else None
    data["charging"] = bat.power_plugged if bat else None

    drive = "C:\\" if os.name == "nt" else "/"
    disk  = psutil.disk_usage(drive)
    data["disk"]          = disk.percent
    data["disk_used_gb"]  = round(disk.used  / 1e9, 1)
    data["disk_total_gb"] = round(disk.total / 1e9, 1)

    return data
