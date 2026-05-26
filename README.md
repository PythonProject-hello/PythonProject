# 시스템 모니터 캐릭터

CPU, RAM 사용률에 따라 캐릭터가 반응하는 시스템 모니터입니다.  
UI는 구현되어 있지 않으므로 자유롭게 추가해주세요.

---

## 실행 방법

```bash
pip install psutil
python main.py
```

---

## 프로젝트 구조

```
Pyject/
  main.py
  config/
    settings.py      # 임계값, 갱신 주기 설정
  core/
    monitor.py       # 시스템 자원 수집
    character.py     # 수집값 → 캐릭터 상태 변환
  ui/                # UI 없음 — 자유롭게 구현
```

---

## 컴퓨팅 자원 추가 방법

`core/monitor.py`의 `get_stats()`에 항목을 추가하면 됩니다.  
아래는 `psutil`로 가져올 수 있는 주요 자원 목록입니다.

### 디스크 사용률
```python
psutil.disk_usage("/").percent        # 루트 파티션 (Linux/Mac)
psutil.disk_usage("C:\\").percent     # C 드라이브 (Windows)
```

### 네트워크 송수신량
```python
net = psutil.net_io_counters()
net.bytes_sent   # 송신 누적 바이트
net.bytes_recv   # 수신 누적 바이트
```
> 누적값이므로 이전 측정값과의 차이로 속도(bps)를 계산해야 합니다.

### 배터리
```python
battery = psutil.sensors_battery()
battery.percent       # 잔량 (%)
battery.power_plugged # 충전 중 여부 (bool)
```
> 데스크탑 등 배터리가 없는 환경에서는 `None`을 반환합니다.

### CPU 온도
```python
temps = psutil.sensors_temperatures()
# 키 이름은 OS/하드웨어마다 다름 (예: "coretemp", "k10temp")
```
> Windows에서는 기본 지원 안 됨. `wmi` 라이브러리 필요.

### 실행 중인 프로세스 수
```python
len(psutil.pids())
```

---

## UI 구현 가이드

`get_stats()`는 dict를 반환하므로 원하는 키를 추가한 뒤 UI에서 읽으면 됩니다.

```python
# core/monitor.py 예시
def get_stats():
    return {
        "cpu":  psutil.cpu_percent(interval=1),
        "ram":  psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("C:\\").percent,  # 추가 예시
    }
```

UI 진입점은 `main.py`이며 `ui/` 폴더 안에 구현을 추가하면 됩니다.

---

## 캐릭터 상태 추가

`core/character.py`의 `MOOD_LABEL`과 `get_mood()`를 수정해 상태를 늘릴 수 있습니다.  
임계값은 `config/settings.py`의 `MOOD_THRESHOLDS`에서 조정합니다.
