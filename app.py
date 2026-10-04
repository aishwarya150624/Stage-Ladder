"""Stage Ladder: a private, offline speaking coach.

Run:   python app.py
Anyone can create an account and log in as often as they like.
Each account keeps its own profile and runs in stage_ladder.db next to this file.
"""
import inspect
import os
import sqlite3
import time
from datetime import datetime

# Keep everything on this laptop: no Gradio telemetry, temp audio inside the project folder.
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".stage_tmp")
os.makedirs(TMP, exist_ok=True)
os.environ.setdefault("GRADIO_TEMP_DIR", TMP)

import gradio as gr  # noqa: E402

import coach  # noqa: E402
import db  # noqa: E402
import ladder  # noqa: E402
import metrics  # noqa: E402
import ui  # noqa: E402
from transcribe import transcribe  # noqa: E402

db.init(os.environ.get("STAGE_DB") or "stage_ladder.db")

N_OUTS = 18  # size of the tuple returned by view()
SESSION_ENDED = "Your session ended. Press Log out, then log in again."


def _state(uid):
    profile = db.get_profile(uid)
    runs = db.list_runs(uid)
    goal = float(profile["filler_goal"] or 6)
    unlocked, streak = ladder.state(runs, goal, int(profile["comfort"] or 1))
    return profile, runs, goal, unlocked, streak


def view(uid, selected=None, message=""):
    """Everything inside the app screen for ONE user, rebuilt from the database."""
    profile, runs, goal, unlocked, streak = _state(uid)
    selected = max(1, min(int(selected or (runs[-1]["rung"] if runs else unlocked)), unlocked))
    last = runs[-1] if runs else None
    labels = ladder.LABELS[:unlocked]
    return (
        ui.header_html(profile, coach.ollama_ready()),
        ui.hero_html(runs, profile, selected),
        ui.ladder_html(selected, unlocked, streak, goal),
        ui.coach_html(last),
        ui.transcript_html(last),
        ui.gauges_html(runs),
        ui.chart_html(runs, goal),
        ui.calm_html(profile, runs),
        f'<div class="sl msg">{ui.e(message)}</div>' if message else '<div class="sl msg"></div>',
        gr.update(choices=labels, value=labels[selected - 1]),
        profile["alias"], profile["event_name"], profile["event_date"],
        profile["filler_goal"], profile["tone"], profile["never_say"], profile["comfort"],
        "",  # the "new password" box is always cleared
    )


NOOP = tuple(gr.update() for _ in range(N_OUTS))


def screens(which, uid=None):
    """Show the login/sign-up screen or the app, and remember which user this browser tab belongs to."""
    return (gr.update(visible=which == "auth"), gr.update(visible=which == "app"), uid)


def msg_html(text):
    return f'<div class="sl msg">{ui.e(text)}</div>'


def valid_password(pw):
    return len(pw or "") >= db.MIN_PASSWORD


def valid_date(text):
    if not text:
        return True
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def entry():
    """Every visit starts at the login screen. Each browser tab logs in separately."""
    return screens("auth")


# ---------- accounts: sign up, log in, log out ----------
def signup(username, pw, pw2, alias, event_name, event_date, goal, tone, comfort):
    def stay(msg):
        return (*screens("auth"), msg_html(msg), *NOOP)

    username = db.norm_username(username)
    if not db.valid_username(username):
        return stay("Choose a username of 3 to 30 characters: letters, numbers, dot, dash or underscore.")
    if db.username_taken(username):
        return stay("That username is taken. Please pick another one, or log in if it is yours.")
    if not valid_password(pw):
        return stay(f"A password needs at least {db.MIN_PASSWORD} characters.")
    if pw != pw2:
        return stay("The two passwords do not match.")
    if not valid_date((event_date or "").strip()):
        return stay("Use the date format YYYY-MM-DD, for example 2026-10-20, or leave it empty.")
    try:
        uid = db.create_user(username, pw)
    except sqlite3.IntegrityError:  # two people picked the same name at the same moment
        return stay("That username is taken. Please pick another one.")
    db.save_profile(uid, alias=(alias or "").strip() or username, event_name=(event_name or "").strip(),
                    event_date=(event_date or "").strip(), filler_goal=float(goal or 6), tone=tone,
                    never_say="", comfort=int(comfort or 1))
    p = db.get_profile(uid)
    start = ladder.start_rung(int(p["comfort"]))
    return (*screens("app", uid), "", *view(uid, start, f"Welcome, {p['alias']}. You start on rung {start}."))


def login(username, pw):
    uid = db.check_login(username, pw)
    if uid is not None:
        return (*screens("app", uid), "", "", *view(uid))
    time.sleep(1)  # slows down guessing
    return (*screens("auth"), msg_html("That username and password do not match."), "", *NOOP)


def logout():
    # also clear the practice topic and recording so the next person on this laptop starts clean
    return (*screens("auth"), "", "", "", None, *NOOP)


# ---------- practice runs ----------
def analyze(audio, topic, rung_label, uid):
    if not db.user_exists(uid):
        yield (*NOOP[:8], msg_html(SESSION_ENDED), *NOOP[9:])
        return
    profile, runs, goal, unlocked, _ = _state(uid)
    rung = min(ladder.parse(rung_label), unlocked)
    if not audio:
        yield view(uid, rung, "Press the microphone, give your talk, then press Analyze. You can also upload a recording.")
        return
    yield view(uid, rung, "Listening to your run. The very first one can take a minute while Whisper loads...")
    try:
        words = transcribe(audio)
    except ImportError:
        yield view(uid, rung, "Whisper is not installed. In your terminal run: pip install faster-whisper")
        return
    except Exception as exc:  # model download, audio decoding, and so on
        err = str(exc)
        if "metadata_errors" in err:  # faster-whisper is newer than the installed audio decoder (av)
            hint = "Your audio decoder is too old. In the terminal run: pip install --upgrade av faster-whisper"
        elif any(w in err.lower() for w in ("connect", "resolve", "huggingface", "offline", "timeout")):
            hint = "The first run needs internet once to download Whisper."
        else:
            hint = "Try a different recording, or run: pip install --upgrade av faster-whisper"
        yield view(uid, rung, f"I could not transcribe that: {err[:160]}. {hint}")
        return
    finally:
        if str(audio).startswith(TMP):
            try:
                os.remove(audio)  # do not keep the recording around
            except OSError:
                pass
    m = metrics.analyze(words)
    if m is None:
        yield view(uid, rung, "I could not hear enough words. Try a run of at least ten seconds.")
        return
    yield view(uid, rung, "Your listener is writing a note...")
    prev = runs[-1]["fillers_per_min"] if runs else None
    note, source, questions = coach.respond(m, prev, profile, rung, topic, len(runs) + 1)
    run_id = db.add_run(uid, topic or profile["event_name"] or "Practice run", rung, m, note, source, questions)
    _, _, _, new_unlocked, _ = _state(uid)
    if new_unlocked > unlocked:
        yield view(uid, new_unlocked, f"Saved as run {run_id}. Rung {new_unlocked} is unlocked!")
    else:
        yield view(uid, rung, f"Saved as run {run_id}.")


# ---------- profile, password, delete ----------
def save_profile(alias, event_name, event_date, goal, tone, never, comfort, new_pw, rung_label, uid):
    if not db.user_exists(uid):
        return (*NOOP[:8], msg_html(SESSION_ENDED), *NOOP[9:])
    sel = ladder.parse(rung_label)
    if not valid_date(event_date.strip()):
        return view(uid, sel, "Use the date format YYYY-MM-DD, for example 2026-10-20.")
    if new_pw and not valid_password(new_pw):
        return view(uid, sel, f"A password needs at least {db.MIN_PASSWORD} characters.")
    db.save_profile(uid, alias=alias.strip(), event_name=event_name.strip(), event_date=event_date.strip(),
                    filler_goal=float(goal or 6), tone=tone, never_say=never, comfort=int(comfort or 1))
    note = "Profile saved."
    if new_pw:
        db.set_password(uid, new_pw)
        note += " Your password was changed."
    return view(uid, sel, note)


def delete_account(confirm, uid):
    if not db.user_exists(uid):
        return (*screens("auth"), "", *NOOP)
    if not confirm:
        return (*screens("app", uid), gr.update(), *view(uid, None, "Tick the box first to confirm you want your account deleted."))
    db.delete_user(uid)
    return (*screens("auth"), msg_html("Your account and all its runs were deleted."), *NOOP)


def on_rung_change(label, uid):
    if not db.user_exists(uid):
        return gr.update()
    _, _, goal, unlocked, streak = _state(uid)
    return ui.ladder_html(ladder.parse(label), unlocked, streak, goal)


# ---------- layout ----------
# Gradio 5 takes css/theme in Blocks(); Gradio 6 takes them in launch().
_OLD_API = "css" in inspect.signature(gr.Blocks.__init__).parameters
_style = dict(css=ui.CSS, theme=ui.make_theme())

with gr.Blocks(title="Stage Ladder", analytics_enabled=False, **(_style if _OLD_API else {})) as demo:
    uid_state = gr.State(None)  # which account this browser tab is logged in to

    # --- light / dark switch, on every screen ---
    with gr.Row(elem_id="theme-row"):
        theme_btn = gr.Button("\U0001F319 Dark mode", elem_id="theme-toggle", size="sm", scale=0)

    # --- log in or create an account (open to anyone, any number of users) ---
    with gr.Column(visible=True) as auth_col:
        gr.HTML(ui.welcome_html("lock"))
        with gr.Tabs():
            with gr.Tab("Log in"):
                with gr.Column(elem_classes="practice"):
                    lock_user = gr.Textbox(label="Username")
                    lock_pin = gr.Textbox(label="Password", type="password")
                    lock_btn = gr.Button("Log in", variant="primary", size="lg")
                    lock_msg = gr.HTML()
                    gr.HTML('<div class="sl empty">New here? Open the "Create account" tab. Anyone can sign up, '
                            'and every account keeps its own runs and profile on this laptop. '
                            'Passwords cannot be recovered, because nothing is stored in the cloud.</div>')
            with gr.Tab("Create account"):
                with gr.Column(elem_classes="practice"):
                    gr.HTML('<div class="sl lab" style="margin:0">YOUR ACCOUNT</div>')
                    with gr.Row():
                        ob_user = gr.Textbox(label="Choose a username")
                        ob_alias = gr.Textbox(label="What should we call you? (optional)")
                    with gr.Row():
                        ob_pin = gr.Textbox(label="Password (at least 4 characters)", type="password")
                        ob_pin2 = gr.Textbox(label="Repeat password", type="password")
                    gr.HTML('<div class="sl lab" style="margin:0">ABOUT YOUR TALK</div>')
                    with gr.Row():
                        ob_event = gr.Textbox(label="Your talk (optional)")
                        ob_date = gr.Textbox(label="Talk date, YYYY-MM-DD (optional)")
                    with gr.Row():
                        ob_goal = gr.Number(label="Filler goal (per minute)", value=6)
                        ob_tone = gr.Radio(["Gentle", "Direct"], value="Gentle", label="Coach tone")
                    ob_comfort = gr.Slider(1, 5, value=1, step=1, label="How comfortable are you speaking?")
                    gr.HTML('<div class="sl lab" style="margin:0">MICROPHONE</div>')
                    gr.HTML(ui.mic_check_html("ob"))
                    ob_mic = gr.Button("Test my microphone")
                    ob_msg = gr.HTML()
                    ob_start = gr.Button("Create account and start practicing", variant="primary", size="lg")

    # --- the app ---
    with gr.Column(visible=False) as app_col:
        header = gr.HTML()
        hero = gr.HTML()
        lock_now_btn = gr.Button("Log out", size="sm", scale=0)
        ladder_box = gr.HTML()
        with gr.Column(elem_classes="practice"):
            gr.HTML('<div class="sl lab" style="margin:0">YOUR TURN ON STAGE</div>')
            topic = gr.Textbox(show_label=False, container=False, lines=1, max_lines=1,
                               placeholder="What are you practicing? For example: Team project update")
            rung = gr.Radio(ladder.LABELS[:1], value=ladder.LABELS[0], show_label=False, container=False)
            audio = gr.Audio(sources=["microphone", "upload"], type="filepath", show_label=False, container=False)
            go = gr.Button("Analyze my run", variant="primary", size="lg")
        status = gr.HTML()
        coach_box = gr.HTML()
        with gr.Row(equal_height=False):
            with gr.Column(scale=7):
                transcript = gr.HTML()
            with gr.Column(scale=4):
                gauges = gr.HTML()
        chart = gr.HTML()
        calm = gr.HTML()
        with gr.Accordion("Microphone check", open=False):
            gr.HTML(ui.mic_check_html("app"))
            app_mic = gr.Button("Test my microphone")
        with gr.Accordion("Your profile (stays on this laptop)", open=False):
            with gr.Row():
                alias = gr.Textbox(label="Name or alias")
                event_name = gr.Textbox(label="Your talk")
                event_date = gr.Textbox(label="Talk date (YYYY-MM-DD)")
            with gr.Row():
                goal = gr.Number(label="Filler goal (per minute)", value=6)
                tone = gr.Radio(["Gentle", "Direct"], value="Gentle", label="Coach tone")
                comfort = gr.Slider(1, 5, value=1, step=1, label="Comfort speaking (sets your starting rung)")
            never = gr.Textbox(label="Things your listener should never say (separate with commas)")
            new_pin = gr.Textbox(label="New password (at least 4 characters, leave empty to keep)", type="password")
            save = gr.Button("Save profile")
        with gr.Accordion("Delete my account", open=False):
            confirm = gr.Checkbox(label="Yes, delete my account, my profile and every run")
            wipe_btn = gr.Button("Delete my account", variant="stop")

    outs = [header, hero, ladder_box, coach_box, transcript, gauges, chart, calm, status, rung,
            alias, event_name, event_date, goal, tone, never, comfort, new_pin]
    assert len(outs) == N_OUTS
    auth = [auth_col, app_col, uid_state]

    demo.load(entry, None, auth)
    demo.load(None, None, None, js=ui.THEME_INIT_JS)
    theme_btn.click(None, None, None, js=ui.THEME_TOGGLE_JS)
    ob_mic.click(None, None, None, js=ui.mic_js("ob"))
    app_mic.click(None, None, None, js=ui.mic_js("app"))
    ob_start.click(signup, [ob_user, ob_pin, ob_pin2, ob_alias, ob_event, ob_date, ob_goal, ob_tone, ob_comfort],
                   auth + [ob_msg] + outs)
    lock_btn.click(login, [lock_user, lock_pin], auth + [lock_msg, lock_pin] + outs)
    lock_pin.submit(login, [lock_user, lock_pin], auth + [lock_msg, lock_pin] + outs)
    lock_now_btn.click(logout, None, auth + [lock_msg, lock_pin, topic, audio] + outs)
    go.click(analyze, [audio, topic, rung, uid_state], outs)
    rung.change(on_rung_change, [rung, uid_state], ladder_box)
    save.click(save_profile, [alias, event_name, event_date, goal, tone, never, comfort, new_pin, rung, uid_state], outs)
    wipe_btn.click(delete_account, [confirm, uid_state], auth + [lock_msg] + outs)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", inbrowser=True, **({} if _OLD_API else _style))