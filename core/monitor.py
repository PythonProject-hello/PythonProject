import os
import time
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
_EXCLUDED_NAMES = {"System Idle Process", "System"}


def get_top_processes(n=5, cpu_threshold=10, mem_threshold=10):
    """CPU/메모리 상위 n개씩(중복 제거) 중 임계값을 넘는 항목만 반환.
    각 항목에 어떤 기준을 넘었는지 tags(["cpu", "mem"])로 표시."""
    usage = {}
    current_pids = set()

    # 최초 호출은 측정 기준점이 없어 모든 프로세스가 0%로 잡힘
    # -> 캐시를 미리 채우고 잠깐 대기해서 시작 직후에도 실제 사용률을 잡음
    if not _proc_cache:
        for p in psutil.process_iter(['pid', 'name']):
            try:
                p.cpu_percent(None)
                _proc_cache[p.info['pid']] = p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(0.2)

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

        if name in _EXCLUDED_NAMES:
            continue

        agg = usage.setdefault(name, {"cpu": 0.0, "mem": 0.0})
        agg["cpu"] += cpu
        agg["mem"] += mem

    for pid in list(_proc_cache):
        if pid not in current_pids:
            del _proc_cache[pid]

    core_count = psutil.cpu_count() or 1
    items = {
        name: {"name": name, "cpu": vals["cpu"] / core_count, "mem": vals["mem"]}
        for name, vals in usage.items()
    }

    top_cpu = sorted(items.values(), key=lambda x: x["cpu"], reverse=True)[:n]
    top_mem = sorted(items.values(), key=lambda x: x["mem"], reverse=True)[:n]

    merged = {item["name"]: item for item in top_cpu + top_mem}

    result = []
    for item in merged.values():
        tags = []
        if item["cpu"] >= cpu_threshold:
            tags.append("cpu")
        if item["mem"] >= mem_threshold:
            tags.append("mem")
        if tags:
            result.append({**item, "tags": tags})

    result.sort(key=lambda x: (x["cpu"], x["mem"]), reverse=True)
    return result
