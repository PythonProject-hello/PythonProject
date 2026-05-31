from config.settings import MOOD_THRESHOLDS

# (stat_key, threshold_key, "ge"=높을때 / "le"=낮을때, (연결형, 종결형))
_CHECKS = [
    ("cpu",     "tired_cpu",   "ge", ("덥고",    "더워요")),
    ("memory",  "tired_memory","ge", ("졸리고",   "졸려요")),
    ("battery", "low_battery", "le", ("배고프고", "배고파요")),
    ("disk",    "tired_disk",  "ge", ("배부르고", "배불러요")),
]

def get_dialogue(stats, thresholds=None):
    if thresholds is None:
        thresholds = MOOD_THRESHOLDS

    complaints = []
    for key, thresh_key, cmp, msgs in _CHECKS:
        val   = stats.get(key)
        thresh = thresholds.get(thresh_key)
        if val is None or thresh is None:
            continue
        if (cmp == "ge" and val >= thresh) or (cmp == "le" and val <= thresh):
            complaints.append(msgs)

    if not complaints:
        return "편안해요"

    parts = [connector for connector, _ in complaints[:-1]]
    parts.append(complaints[-1][1])
    return " ".join(parts)
