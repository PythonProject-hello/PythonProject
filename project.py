import psutil
def project_data():
    cpu_percent=psutil.cpu_percent(interval=1)
    cpu_freq=psutil.cpu_freq()

    mem=psutil.virtual_memory()
    mem_percent=mem.percent
    mem_used_gb=round(mem.used/1e9,1)
    mem_total_gb=round(mem.total/1e9,1)

    bat=psutil.sensors_battery()
    bat_percent=bat.percent if bat else None
    bat_charging=bat.power_plugged if bat else None

    disk=psutil.disk_usage("/")
    disk_percent=disk.percent

    mem_available_gb=round(mem.available/1e9,1)
    return{
        "cpu":cpu_percent,
         "cpu_freq": round(cpu_freq.current / 1000, 2) if cpu_freq else None,
        "memory": mem_percent,
        "memory_used_gb": mem_used_gb,
        "memory_total_gb": mem_total_gb,
        "battery": bat_percent,
        "charging": bat_charging,
        "disk": disk_percent,
        "memory_available_gb": mem_available_gb
    }
if __name__ == "__main__":
    data = project_data()
    print("CPU 사용률:", data["cpu"], "%")
    print("CPU 클럭:", data["cpu_freq"], "GHz")
    print("메모리 사용률:", data["memory"], "%")
    print("배터리 잔량:", data["battery"], "%")
    if data["charging"]:
        print("충전 상태: 충전중입니다")
    else:
        print("충전 상태: 충전중이 아닙니다")
    print("디스크 사용률:", data["disk"], "%")
    print("램 남은 용량:", data["memory_available_gb"], "GB")