# 대충 설명

CPU, RAM 사용률에 따라 캐릭터가 반응하는 시스템 모니터입니다.

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
    character.py     # 수집값 → 캐릭터 대사 변환
  ui/
    app.py           # 메인 화면(임시 UI)
    settings_window.py # 설정창(임시 UI)
```

---



## project_data() 가져오기

```python
from core.monitor import project_data

stats = project_data()
print(stats["cpu"])      # CPU 사용률 (%)
print(stats["memory"])   # RAM 사용률 (%)
print(stats["battery"])  # 배터리 잔량 (%), 배터리 없으면 None
print(stats["disk"])     # 디스크 사용률 (%)
```

반환 키 전체 목록:

| 키 | 설명 | 단위 |
|----|------|------|
| `cpu` | CPU 사용률 | % |
| `cpu_freq` | CPU 클럭 | GHz |
| `memory` | RAM 사용률 | % |
| `memory_used_gb` | RAM 사용량 | GB |
| `memory_total_gb` | RAM 전체 용량 | GB |
| `memory_available_gb` | RAM 여유 용량 | GB |
| `battery` | 배터리 잔량 | % (없으면 None) |
| `charging` | 충전 중 여부 | bool (없으면 None) |
| `disk` | 디스크 사용률 | % |

---

## 캐릭터 대사 추가

`core/character.py`의 `_CHECKS`에 항목을 추가하면 됩니다.  
임계값은 `config/settings.py`의 `MOOD_THRESHOLDS`에서 조정합니다.

```python
# (stat_key, threshold_key, "ge"=높을때 / "le"=낮을때, (연결형, 종결형))
_CHECKS = [
    ("cpu",     "tired_cpu",   "ge", ("덥고",    "더워요")),
    ("memory",  "tired_memory","ge", ("졸리고",   "졸려요")),
    ("battery", "low_battery", "le", ("배고프고", "배고파요")),
    ("disk",    "tired_disk",  "ge", ("배부르고", "배불러요")),
]
```
