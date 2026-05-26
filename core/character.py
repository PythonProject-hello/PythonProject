from config.settings import MOOD_THRESHOLDS

def get_mood(stats):
    cpu = stats["cpu"]
    ram = stats["ram"]

    if cpu >= MOOD_THRESHOLDS["panic_cpu"] or ram >= MOOD_THRESHOLDS["panic_ram"]:
        return "panicking"
    elif cpu >= MOOD_THRESHOLDS["tired_cpu"] or ram >= MOOD_THRESHOLDS["tired_ram"]:
        return "tired"
    else:
        return "normal"

MOOD_LABEL = {
    "normal":    "😊 여유로움",
    "tired":     "😓 힘들어요",
    "panicking": "😱 살려줘!!",
}
