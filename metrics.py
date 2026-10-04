"""Speech metrics in plain Python. No AI is involved, so the numbers can be trusted."""
import re

FILLER_WORDS = {"um", "umm", "uh", "uhh", "er", "erm", "ah", "hmm", "mm", "mhm"}
FILLER_PHRASES = {("you", "know"), ("i", "mean")}
PAUSE_MARK = 1.5          # seconds; longer gaps are shown in the transcript
SWEET_SPOT = (110, 150)   # words per minute that are easy to follow


def _norm(text):
    return re.sub(r"[^a-z']", "", text.lower())


def _fmt(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def analyze(words):
    """words: [{"text", "start", "end"}]. Returns a metrics dict or None if too short."""
    clean = [w for w in words if _norm(w["text"])]
    if len(clean) < 5:
        return None
    t0, t1 = clean[0]["start"], clean[-1]["end"]
    dur = t1 - t0
    if dur < 5:
        return None
    norms = [_norm(w["text"]) for w in clean]

    # Opening sentence: first words up to the first . ? or !
    open_end = None
    for i, w in enumerate(clean[:25]):
        if w["text"].rstrip().endswith((".", "?", "!")):
            open_end = i
            break

    tokens, filler_pos, pause_pos = [], [], []
    fillers, longest = 0, 0.0
    i = 0
    while i < len(clean):
        w = clean[i]
        if i > 0:
            gap = max(0.0, w["start"] - clean[i - 1]["end"])
            longest = max(longest, gap)
            if gap >= PAUSE_MARK:
                tokens.append(["pause", f"{gap:.1f}s pause"])
                pause_pos.append([round((clean[i - 1]["end"] - t0) / dur * 100, 2),
                                  round(max(gap / dur * 100, 1.0), 2)])
        if i + 1 < len(clean) and (norms[i], norms[i + 1]) in FILLER_PHRASES:
            tokens.append(["filler", f'{w["text"]} {clean[i + 1]["text"]}'.strip(" ,.")])
            filler_pos.append(round((w["start"] - t0) / dur * 100, 2))
            fillers += 1
            i += 2
        elif norms[i] in FILLER_WORDS:
            tokens.append(["filler", w["text"].strip(" ,.")])
            filler_pos.append(round((w["start"] - t0) / dur * 100, 2))
            fillers += 1
            i += 1
        else:
            tokens.append(["w", w["text"]])
            i += 1

    # Mark a clean opening sentence as a strong moment.
    if open_end is not None and open_end >= 3:
        head = tokens[: open_end + 1]
        if all(k == "w" for k, _ in head):
            sentence = " ".join(t for _, t in head)
            tokens = [["strong", sentence]] + tokens[open_end + 1:]

    minutes = dur / 60
    wpm = round(len(clean) / minutes)
    if wpm < SWEET_SPOT[0]:
        note = "a little slow"
    elif wpm > SWEET_SPOT[1]:
        note = "a little fast"
    else:
        note = "in your sweet spot"
    return {
        "duration": round(dur, 1),
        "duration_text": _fmt(dur),
        "words": len(clean),
        "wpm": wpm,
        "pace_note": note,
        "fillers": fillers,
        "fillers_per_min": round(fillers / minutes, 1),
        "longest_pause": round(longest, 1),
        "tokens": tokens,
        "filler_pos": filler_pos,
        "pause_pos": pause_pos,
        "axis": ["0:00", _fmt(dur / 3), _fmt(2 * dur / 3), _fmt(dur)],
        "transcript": " ".join(w["text"] for w in clean),
    }
