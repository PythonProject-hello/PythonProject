from config.settings import MOOD_THRESHOLDS

def get_mood(stats, thresholds=None):
    if thresholds is None:
        thresholds = MOOD_THRESHOLDS

    cpu = stats["cpu"]
    ram = stats["ram"]

    if cpu >= thresholds["panic_cpu"] or ram >= thresholds["panic_ram"]:
        return "panicking"
    elif cpu >= thresholds["tired_cpu"] or ram >= thresholds["tired_ram"]:
        return "tired"
    else:
        return "normal"

MOOD_LABEL = {
    "normal":    "😊 여유로움",
    "tired":     "😓 힘들어요",
    "panicking": "😱 살려줘!!",
}
