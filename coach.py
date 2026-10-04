"""The kind listener. Gemma 3 1B writes short notes through Ollama; a built-in fallback
keeps the app useful if Ollama is not running. The numbers themselves never come from the AI."""
import os
import re

MODEL = os.environ.get("STAGE_MODEL", "gemma3:1b")

TOUGH_FALLBACK = [
    "What is the biggest risk you have not addressed yet?",
    "How will you know this actually worked?",
    "What would you do differently if you had half the time?",
    "Who disagrees with this, and what would they say?",
]


def ollama_ready():
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False


def _chat(system, user, max_tokens=140):
    import ollama
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        options={"temperature": 0.6, "num_predict": max_tokens},
    )
    return r["message"]["content"]


def _never(profile):
    return [p.strip().lower() for p in re.split(r"[,\n]", profile.get("never_say", "")) if p.strip()]


def _clean(text, banned, sentences=3):
    text = re.sub(r"[*#_`>]+", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    text = " ".join(parts[:sentences]).strip()
    if not text or any(b in text.lower() for b in banned):
        return None
    return text


def _fallback_note(m, prev, profile, goal):
    direct = profile.get("tone", "Gentle") == "Direct"
    if prev is None:
        first = "You finished your first run, which is the hardest one."
    elif m["fillers_per_min"] < prev:
        first = f"Your fillers dropped from {prev:g} to {m['fillers_per_min']:g} a minute."
    elif m["fillers_per_min"] == prev:
        first = f"Your fillers held steady at {prev:g} a minute."
    else:
        first = f"Fillers rose to {m['fillers_per_min']:g} a minute this time, which happens on a busy day."
    if m["fillers_per_min"] <= goal:
        first += f" That is under your goal of {goal:g}."
    if m["pace_note"] == "in your sweet spot":
        pace = f"Your pace of {m['wpm']} words a minute is easy to follow."
    elif m["pace_note"] == "a little fast":
        pace = f"You were a little quick at {m['wpm']} words a minute, so let the end of each sentence land."
    else:
        pace = f"You were a little slow at {m['wpm']} words a minute, so try lifting the energy a notch."
    tip = ("Next time, replace each filler with a silent breath." if direct
           else "Next time, try one slow breath after your opening sentence instead of a filler.")
    return " ".join([first, pace, tip])


def respond(m, prev, profile, rung, topic, run_number):
    """Returns (feedback, source, questions). source is 'gemma', 'fallback', or 'numbers'."""
    goal = float(profile.get("filler_goal") or 6)
    banned = _never(profile)
    if rung == 1:
        return ("Rung 1 is numbers only, with no judgment. Move up when you want a listener.",
                "numbers", [])

    tone = "direct and brief" if (rung == 4 or profile.get("tone") == "Direct") else "gentle and warm"
    system = (
        f"You are a kind speaking coach. Your tone is {tone}. Reply in at most three short "
        "sentences. Name one thing the speaker did well using their numbers. Suggest exactly one "
        "thing to try next time. Never judge, never diagnose, never use exclamation marks."
    )
    if banned:
        system += " Never say or imply: " + "; ".join(banned) + "."
    facts = (
        f"Talk topic: {topic or 'not given'}. Run number {run_number}. Pace {m['wpm']} words per "
        f"minute (easy range is 110 to 150). Fillers {m['fillers_per_min']} per minute. Longest "
        f"pause {m['longest_pause']} seconds. Their goal is under {goal:g} fillers a minute."
    )
    if prev is not None:
        facts += f" Their previous run had {prev:g} fillers a minute."

    source = "gemma"
    try:
        note = _clean(_chat(system, facts), banned)
        if note is None:
            raise ValueError("unusable note")
    except Exception:
        note, source = _fallback_note(m, prev, profile, goal), "fallback"

    questions = []
    if rung >= 3:
        n = 1 if rung == 3 else 2
        try:
            raw = _chat(
                "You are an audience member. Ask fair but challenging questions about the talk. "
                "One sentence per question, one question per line, no numbering, no preamble.",
                f"Talk topic: {topic or 'a work update'}. Excerpt: {m['transcript'][:700]}\nAsk {n}.",
                max_tokens=100,
            )
            lines = [re.sub(r"^[\-\d.\s*]+", "", ln).strip() for ln in raw.splitlines() if "?" in ln]
            questions = [q for q in lines if len(q) > 12][:n]
        except Exception:
            questions = []
        for q in TOUGH_FALLBACK:
            if len(questions) >= n:
                break
            if q not in questions:
                questions.append(q)
    return note, source, questions
