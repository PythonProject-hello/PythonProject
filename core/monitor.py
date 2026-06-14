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


_proc_cache = {}


def get_top_processes(n=5):
    """CPU 사용률 기준 상위 n개 프로그램(이름으로 합산)을 반환."""
    usage = {}
    current_pids = set()

    for p in psutil.process_iter(['pid', 'name']):
        pid = p.info['pid']
        current_pids.add(pid)

        proc = _proc_cache.get(pid)
        if proc is None:
            try:
                p.cpu_percent(None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            _proc_cache[pid] = p
            continue  # 첫 측정은 기준점 설정용

        try:
            cpu  = proc.cpu_percent(None)
            mem  = proc.memory_percent()
            name = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        agg = usage.setdefault(name, {"cpu": 0.0, "mem": 0.0})
        agg["cpu"] += cpu
        agg["mem"] += mem

    for pid in list(_proc_cache):
        if pid not in current_pids:
            del _proc_cache[pid]

    core_count = psutil.cpu_count() or 1
    items = [
        {"name": name, "cpu": vals["cpu"] / core_count, "mem": vals["mem"]}
        for name, vals in usage.items()
    ]
    items.sort(key=lambda x: x["cpu"], reverse=True)
    return items[:n]
