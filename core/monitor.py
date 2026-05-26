import psutil

_prev_net = None

def get_stats():
    global _prev_net

    stats = {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("C:\\").percent,
    }

    # 네트워크 — 이전 측정값과의 차이로 수신 사용률 근사
    cur = psutil.net_io_counters()
    if _prev_net is not None:
        recv_kb = (cur.bytes_recv - _prev_net.bytes_recv) / 1024
        stats["network"] = round(recv_kb, 1)
    else:
        stats["network"] = 0.0
    _prev_net = cur

    # 배터리 — 없는 환경이면 None
    bat = psutil.sensors_battery()
    stats["battery"] = bat.percent if bat else None

    return stats
