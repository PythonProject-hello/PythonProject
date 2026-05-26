import psutil

_prev_net = None

def get_stats():
    global _prev_net

    cpu_freq = psutil.cpu_freq()
    mem  = psutil.virtual_memory()
    bat  = psutil.sensors_battery()
    disk = psutil.disk_usage("C:\\")

    stats = {
        "cpu":              psutil.cpu_percent(interval=1),
        "cpu_freq":         round(cpu_freq.current / 1000, 2) if cpu_freq else None,
        "ram":              mem.percent,
        "ram_used_gb":      round(mem.used / 1e9, 1),
        "ram_total_gb":     round(mem.total / 1e9, 1),
        "ram_available_gb": round(mem.available / 1e9, 1),
        "disk":             disk.percent,
        "battery":          bat.percent if bat else None,
        "charging":         bat.power_plugged if bat else None,
    }

    cur = psutil.net_io_counters()
    if _prev_net is not None:
        stats["network"] = round((cur.bytes_recv - _prev_net.bytes_recv) / 1024, 1)
    else:
        stats["network"] = 0.0
    _prev_net = cur

    return stats
