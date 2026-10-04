"""Ladder progress: which rung is unlocked, and how close you are to the next one."""
RUNGS = [
    (1, "Alone", "numbers only"),
    (2, "Friendly listener", "kind feedback"),
    (3, "Tough question", "one hard question"),
    (4, "Skeptical room", "a firmer room"),
]
LABELS = [f"{n}. {title}" for n, title, _ in RUNGS]
CAPTIONS = {
    1: "Alone on stage. Nobody is listening yet",
    2: "A friendly audience is listening",
    3: "A curious audience is waiting with a question",
    4: "A skeptical room is watching closely",
}


def start_rung(comfort):
    return 1 if comfort <= 2 else (2 if comfort <= 4 else 3)


def state(runs, goal, comfort):
    """Returns (unlocked_rung, streak). Two runs in a row at the top rung under goal unlock the next."""
    unlocked, streak = start_rung(comfort), 0
    for r in runs:
        if r["rung"] != unlocked:
            continue
        streak = streak + 1 if r["fillers_per_min"] <= goal else 0
        if streak >= 2 and unlocked < 4:
            unlocked, streak = unlocked + 1, 0
    return unlocked, streak


def parse(label):
    try:
        return int(str(label).strip()[0])
    except (ValueError, IndexError):
        return 1
