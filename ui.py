"""HTML pieces, palettes and theme. Pick a light palette with STAGE_THEME=sunset | ocean;
STAGE_THEME=dusk starts in dark mode. The Dark mode button in the app switches any time."""
import html
import os
from datetime import date, datetime

import random

from ladder import CAPTIONS, RUNGS
from metrics import SWEET_SPOT

e = html.escape

PALETTES = {
    # soft lavender to peach, violet and coral accents
    "sunset": dict(
        page="linear-gradient(160deg,#E9E1FF 0%,#F6E3F5 50%,#FFE6D8 100%)", card="rgba(255,255,255,.88)",
        border="rgba(108,77,255,.16)", text="#251C4D", muted="#6D6590", accent="#6C4DFF", accent2="#B05CFF",
        accent_soft="#ECE6FF", on_accent="#FFFFFF", hero="linear-gradient(120deg,#6C4DFF 0%,#B05CFF 55%,#FF7A59 100%)",
        filler_bg="#FFE7BF", filler_text="#8A4B00", pause_bg="#FFDCE6", pause_text="#B0194A", strong_bg="#D8F5E7",
        good="#1E9E6A", good_bg="#D8F5E7", warm_bg="#FFE7BF", warm_text="#8A4B00", input_bg="#F5F1FF",
        input_border="#D6CCF6", track="#E7E1F8", shadow="rgba(90,60,170,.14)", stroke="#6C4DFF", dot_ring="#FFFFFF", crowd="#2F1A66", ctl="#FFFFFF"),
    # airy teal and blue with warm gold
    "ocean": dict(
        page="linear-gradient(160deg,#D8F0F2 0%,#DCE8FB 55%,#E9E4FA 100%)", card="rgba(255,255,255,.86)",
        border="rgba(14,130,150,.18)", text="#12324A", muted="#5A7790", accent="#0E8FA0", accent2="#3B6FE0",
        accent_soft="#DDF1F5", on_accent="#FFFFFF", hero="linear-gradient(115deg,#0B8FA3 0%,#2F6FE0 55%,#5B5BDB 100%)",
        filler_bg="#FFEBC2", filler_text="#8A5200", pause_bg="#FFDDE3", pause_text="#B0243F", strong_bg="#D5F3E6",
        good="#12906A", good_bg="#D5F3E6", warm_bg="#FFEBC2", warm_text="#8A5200", input_bg="#EEF6FA",
        input_border="#C7DCE6", track="#DCE8F0", shadow="rgba(20,90,130,.14)", stroke="#0E8FA0", dot_ring="#FFFFFF", crowd="#0A2A52", ctl="#FFFFFF"),
    # a mid-dark slate-indigo with warm accents, easy on the eyes
    "dusk": dict(
        page="linear-gradient(160deg,#2C3568 0%,#3B3170 55%,#4A3470 100%)", card="rgba(255,255,255,.10)",
        border="rgba(255,255,255,.18)", text="#F4F2FF", muted="#BDB9E4", accent="#FFB547", accent2="#FF7A59",
        accent_soft="rgba(255,181,71,.16)", on_accent="#2A1600", hero="linear-gradient(120deg,#5B6CFF 0%,#9B5CFF 55%,#FF7AA8 100%)",
        filler_bg="rgba(255,181,71,.22)", filler_text="#FFD58A", pause_bg="rgba(255,122,168,.22)", pause_text="#FFB0C8",
        strong_bg="rgba(94,230,192,.20)", good="#6EE7C2", good_bg="rgba(94,230,192,.18)", warm_bg="rgba(255,181,71,.2)",
        warm_text="#FFD58A", input_bg="rgba(255,255,255,.08)", input_border="rgba(255,255,255,.22)",
        track="rgba(255,255,255,.14)", shadow="rgba(10,8,40,.30)", stroke="#FFB547", dot_ring="#3B3170", crowd="#15123A", ctl="rgba(255,255,255,.10)"),
}
THEME = os.environ.get("STAGE_THEME", "ocean")
# Dark mode: the "dusk" palette. STAGE_THEME=dusk simply starts in dark mode (light mode then uses "ocean").
DEFAULT_DARK = THEME == "dusk"
LIGHT = PALETTES["ocean" if DEFAULT_DARK else THEME] if (DEFAULT_DARK or THEME in PALETTES) else PALETTES["sunset"]
DARK = PALETTES["dusk"]
P = DARK if DEFAULT_DARK else LIGHT  # kept for any code that reads the starting palette


def _vars(p):
    return "".join(f"--{k.replace('_', '-')}:{v};" for k, v in p.items())


def _root(light, dark, start_dark):
    """CSS variables. The page follows the system unless the person has pressed the toggle
    (the toggle puts class sl-dark or sl-light on <html>)."""
    if start_dark:
        return f":root{{{_vars(dark)}color-scheme:dark}}html.sl-light{{{_vars(light)}color-scheme:light}}"
    return (f":root{{{_vars(light)}color-scheme:light}}"
            f"@media (prefers-color-scheme:dark){{html:not(.sl-light){{{_vars(dark)}color-scheme:dark}}}}"
            f"html.sl-dark{{{_vars(dark)}color-scheme:dark}}")


STATIC = """
footer{display:none!important}
.gradio-container{max-width:960px!important;margin:auto!important;background:transparent!important;color:var(--text);
 font-family:'Segoe UI',system-ui,-apple-system,Carlito,'DejaVu Sans',sans-serif!important}
.block,.form{background:transparent!important;border:none!important;box-shadow:none!important}
.sl,.sl *{box-sizing:border-box}.sl{color:var(--text)}
.card{background:var(--card);border:1px solid var(--border);border-radius:22px;padding:22px 26px;box-shadow:0 10px 30px var(--shadow);backdrop-filter:blur(10px)}
.lab{font-size:12px;letter-spacing:.1em;color:var(--muted);font-weight:700;margin-bottom:10px}
.top{display:flex;align-items:center;justify-content:space-between;padding:20px 4px 6px;flex-wrap:wrap;gap:10px}
.logo{display:flex;align-items:center;gap:10px;font-size:22px;font-weight:800;color:var(--text)}
.mark{display:inline-flex;align-items:flex-end;gap:3px;height:24px}.mark i{display:block;width:7px;border-radius:3px;background:linear-gradient(180deg,var(--accent),var(--accent2))}
.meta{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted);flex-wrap:wrap}
.chip{padding:5px 12px;border-radius:99px;background:var(--accent-soft);color:var(--text);font-weight:600;font-size:13px;border:1px solid var(--border)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;background:var(--good)}.dot.off{background:#B9BCD3}
.herobox{position:relative;overflow:hidden;border-radius:26px;padding:30px 34px 118px;margin:10px 0 4px;background:var(--hero);color:#fff;box-shadow:0 18px 40px var(--shadow)}
.herobox .row{position:relative;z-index:3;display:flex;align-items:flex-start;justify-content:space-between;gap:20px;flex-wrap:wrap}
.eyebrow{font-size:12px;letter-spacing:.14em;font-weight:700;opacity:.9;color:#fff}
.herobox h1{font-size:34px;font-weight:800;margin:6px 0 6px;color:#fff;letter-spacing:-.01em;line-height:1.15}
.herobox p{font-size:16px;margin:0;opacity:.92;color:#fff}
.beam{position:absolute;top:-30px;width:230px;height:330px;margin-left:-115px;transform-origin:50% 0;z-index:1;pointer-events:none;
 background:linear-gradient(rgba(255,255,255,.50),rgba(255,255,255,0) 90%);clip-path:polygon(43% 0,57% 0,100% 100%,0 100%);filter:blur(5px)}
.b1{left:58%;animation:sway 6.5s ease-in-out infinite alternate}.b2{left:72%;animation:sway2 8s ease-in-out infinite alternate}
.b3{left:44%;opacity:.55;animation:sway 9s ease-in-out infinite alternate-reverse}
@keyframes sway{from{transform:rotate(-16deg)}to{transform:rotate(12deg)}}
@keyframes sway2{from{transform:rotate(14deg)}to{transform:rotate(-12deg)}}
.pool{position:absolute;right:130px;bottom:58px;width:240px;height:46px;border-radius:50%;z-index:1;background:radial-gradient(ellipse,rgba(255,255,255,.55),rgba(255,255,255,0) 70%);animation:pulse 3s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.55;transform:scale(.92)}50%{opacity:1;transform:scale(1.06)}}
.mic{display:block;height:150px;width:auto;margin-top:-8px}
.ring{transform-box:fill-box;transform-origin:center;animation:ripple 2.6s ease-out infinite;opacity:0}
.ring:nth-of-type(2){animation-delay:.87s}.ring:nth-of-type(3){animation-delay:1.74s}
@keyframes ripple{0%{transform:scale(.7);opacity:.7}100%{transform:scale(2);opacity:0}}
.crowd{position:absolute;left:0;right:0;bottom:0;height:104px;z-index:2;pointer-events:none}
.pp{position:absolute;transform:translate(-50%,0);animation:bob 3.4s ease-in-out infinite;animation-delay:var(--d)}
.pp i{display:block;width:var(--s);height:var(--s);border-radius:50%;background:var(--crowd);margin:0 auto;box-shadow:0 -2px 0 var(--rim)}
.pp b{display:block;width:calc(var(--s)*2.3);height:calc(var(--s)*1.5);border-radius:50% 50% 0 0;background:var(--crowd);margin-top:2px;box-shadow:0 -2px 0 var(--rim)}
@keyframes bob{0%,100%{transform:translate(-50%,0)}50%{transform:translate(-50%,-5px)}}
.capt{position:absolute;left:0;right:0;bottom:104px;text-align:center;font-size:13px;color:rgba(255,255,255,.92);z-index:3;letter-spacing:.02em}
.stagebox{display:flex;align-items:center;gap:6px}
.glass{background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.4);border-radius:18px;padding:12px 20px;text-align:center;min-width:130px;backdrop-filter:blur(6px)}
.glass b{display:block;font-size:34px;line-height:1.05;font-weight:800;color:#fff}.glass small{font-size:12px;opacity:.9;color:#fff}
.steps{display:grid;grid-template-columns:repeat(4,1fr);position:relative}
.steps:before{content:"";position:absolute;left:12.5%;right:12.5%;top:19px;height:4px;border-radius:4px;background:var(--line)}
.step{text-align:center;position:relative}
.circle{width:40px;height:40px;border-radius:50%;margin:0 auto 8px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;
 background:var(--card);color:var(--accent);border:2px solid var(--accent);position:relative}
.step.done .circle{background:var(--good);color:#fff;border-color:var(--good)}
.step.now .circle{background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);border:none;box-shadow:0 0 0 6px var(--accent-soft);animation:glow 2.4s ease-in-out infinite}
@keyframes glow{0%,100%{box-shadow:0 0 0 5px var(--accent-soft)}50%{box-shadow:0 0 0 11px rgba(255,255,255,0)}}
.step.lock .circle{background:var(--track);color:var(--muted);border-color:transparent}
.step b{display:block;font-size:14px;color:var(--text)}.step small{font-size:12px;color:var(--muted)}.step.lock b{color:var(--muted)}
.unlock{margin-top:16px;display:flex;align-items:center;gap:12px;font-size:13px;color:var(--muted)}
.bar{flex:1;min-width:60px;height:8px;border-radius:8px;background:var(--track);overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:8px}
.tx{font-size:19px;line-height:2;color:var(--text)}
.f{background:var(--filler-bg);color:var(--filler-text);border-radius:8px;padding:2px 9px;font-weight:700}
.p{background:var(--pause-bg);color:var(--pause-text);border-radius:8px;padding:2px 9px;font-size:15px;font-weight:700}
.g{background:var(--strong-bg);border-radius:6px;padding:2px 5px}
.legend{display:flex;gap:18px;margin-top:10px;font-size:13px;color:var(--muted);flex-wrap:wrap;align-items:center}
.tl{position:relative;height:16px;margin:16px 0 6px;background:var(--track);border-radius:10px}.tl i{position:absolute;top:0;width:5px;height:16px;border-radius:3px;background:#F2A33A}
.tl i.pz{background:#E8588A;border-radius:5px}
.ax{display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}
.tile{padding:16px 20px 16px 24px;position:relative;overflow:hidden}.tile+.tile{margin-top:12px}
.tile:before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--bar)}
.tile small{font-size:13px;color:var(--muted);font-weight:600}
.tile .n{font-size:36px;font-weight:800;color:var(--text);line-height:1.1;margin:4px 0 8px}.tile .n u{text-decoration:none;font-size:14px;font-weight:600;color:var(--muted);margin-left:5px}
.tag{display:inline-block;padding:3px 11px;border-radius:99px;font-size:12px;font-weight:700;background:var(--good-bg);color:var(--good)}.tag.warm{background:var(--warm-bg);color:var(--warm-text)}
.range{position:relative;height:9px;border-radius:9px;background:var(--track);margin:2px 0 10px}.range i{position:absolute;top:0;height:9px;background:var(--good);opacity:.45;border-radius:9px}
.range b{position:absolute;top:-4px;width:7px;height:17px;border-radius:4px;background:var(--accent)}
.coach{display:flex;gap:16px;align-items:flex-start}
.av{width:48px;height:48px;border-radius:50%;flex-shrink:0;background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);display:flex;align-items:center;justify-content:center;font-size:22px}
.coach p{font-size:19px;line-height:1.65;color:var(--text);margin:0}.src{font-size:12px;color:var(--muted);margin-top:10px}
.qs{margin-top:16px;padding:12px 16px;border-radius:14px;background:var(--accent-soft);border-left:5px solid var(--accent);font-size:16px;color:var(--text);line-height:1.6}
.qs small{display:block;font-size:11px;letter-spacing:.1em;color:var(--muted);font-weight:700;margin-bottom:4px}
.calm{padding:16px 22px;border-radius:18px;background:var(--good-bg);border:1px solid var(--border);font-size:16px;color:var(--text)}
.calm b{color:var(--good)}
.empty{color:var(--muted);font-size:16px;line-height:1.7}.empty b{color:var(--text)}
.msg{min-height:22px;font-size:14px;color:var(--text);padding:0 6px;font-weight:600}
.practice{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:22px!important;padding:22px 24px!important;
 box-shadow:0 10px 30px var(--shadow)!important;gap:14px!important;border-top:5px solid var(--accent)!important}
.practice .block,.practice .styler{background:transparent!important}
.practice textarea,.practice input[type=text],.practice input[type=password],.practice input[type=number]{background:var(--input-bg)!important;color:var(--text)!important;border:1px solid var(--input-border)!important;border-radius:14px!important;padding:12px 14px!important;font-size:16px!important}
.practice textarea{min-height:48px!important}
.miccard{background:var(--accent-soft);border:1px solid var(--border);border-radius:16px;padding:14px 16px}
.micmsg{font-size:15px;color:var(--text);line-height:1.5;margin-bottom:10px}
.miclevel{height:12px;border-radius:12px;background:var(--track);overflow:hidden}
.miclevel i{display:block;height:100%;width:0;border-radius:12px;background:linear-gradient(90deg,var(--good),var(--accent));transition:width .08s linear}
.gradio-container .label-wrap,.gradio-container .accordion{background:var(--card)!important;border-radius:16px!important;color:var(--text)!important}
"""

STATIC += "@media (prefers-reduced-motion:reduce){*{animation:none!important}}\n"
STATIC += "#theme-row{justify-content:flex-end!important;padding:6px 4px 0}#theme-toggle{min-width:0!important;width:auto!important}\n"
CSS = _root(LIGHT, DARK, DEFAULT_DARK) + STATIC


# Runs in the browser. window.stageTheme(dark, save) switches the look and the button label.
_THEME_FN = """
window.stageTheme = (dark, save) => {
  const root = document.documentElement;
  root.classList.toggle('sl-dark', dark);
  root.classList.toggle('sl-light', !dark);
  document.body.classList.toggle('dark', dark);   // keeps Gradio's own widgets in step
  if (save) { try { localStorage.setItem('stage-theme', dark ? 'dark' : 'light'); } catch (e) {} }
  const b = document.getElementById('theme-toggle');
  if (b) b.textContent = dark ? '\\u2600\\uFE0F Light mode' : '\\u{1F319} Dark mode';
};
"""

THEME_INIT_JS = "() => {" + _THEME_FN + """
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const pick = () => {
    let saved = null;
    try { saved = localStorage.getItem('stage-theme'); } catch (e) {}
    return saved ? saved === 'dark' : (%s || mq.matches);
  };
  window.stageTheme(pick(), false);
  mq.addEventListener('change', () => { let s = null; try { s = localStorage.getItem('stage-theme'); } catch (e) {} if (!s) window.stageTheme(pick(), false); });
}""" % ("true" if DEFAULT_DARK else "false")

THEME_TOGGLE_JS = "() => {" + _THEME_FN + """
  window.stageTheme(!document.documentElement.classList.contains('sl-dark'), true);
}"""


def make_theme():
    """Gradio control colors. They point at the CSS variables above, so light and dark mode switch live."""
    import gradio as gr

    def v(k):
        return f"var(--{k.replace('_', '-')})"

    vals = {
        "body_background_fill": v("page"), "body_text_color": v("text"), "body_text_color_subdued": v("muted"),
        "background_fill_primary": v("ctl"), "background_fill_secondary": "transparent",
        "block_background_fill": "transparent", "block_border_color": v("input_border"), "block_shadow": "none",
        "block_label_background_fill": "transparent", "block_label_text_color": v("muted"),
        "block_title_text_color": v("muted"), "border_color_primary": v("input_border"),
        "input_background_fill": v("input_bg"), "input_border_color": v("input_border"), "input_shadow": "none",
        "panel_background_fill": "transparent", "panel_border_color": v("input_border"),
        "button_primary_background_fill": "linear-gradient(135deg,var(--accent),var(--accent2))",
        "button_primary_background_fill_hover": "linear-gradient(135deg,var(--accent2),var(--accent))",
        "button_primary_text_color": v("on_accent"), "button_primary_border_color": "transparent",
        "button_secondary_background_fill": v("ctl"), "button_secondary_background_fill_hover": v("accent_soft"),
        "button_secondary_text_color": v("text"), "button_secondary_border_color": v("input_border"),
        "button_cancel_background_fill": v("pause_bg"), "button_cancel_background_fill_hover": v("pause_bg"),
        "button_cancel_text_color": v("pause_text"), "button_cancel_border_color": v("pause_bg"),
        "checkbox_background_color": v("ctl"), "checkbox_label_background_fill": v("ctl"),
        "checkbox_label_background_fill_selected": v("accent_soft"), "checkbox_label_text_color": v("text"),
        "checkbox_label_text_color_selected": v("text"), "checkbox_border_color": v("input_border"),
        "slider_color": v("accent"), "color_accent_soft": v("accent_soft"),
    }
    settings = {}
    for k, val in vals.items():
        settings[k] = val
        settings[k + "_dark"] = val
    return gr.themes.Base(primary_hue="violet", neutral_hue="slate", radius_size="lg",
                          font=("Segoe UI", "system-ui", "sans-serif")).set(**settings)


def _days(profile):
    try:
        d = datetime.strptime(profile.get("event_date", ""), "%Y-%m-%d").date()
    except ValueError:
        return None
    return (d - date.today()).days


def header_html(profile, ollama_ok):
    days = _days(profile)
    when = "" if days is None else (f"Talk in {days} days" if days > 1 else "Talk tomorrow" if days == 1
                                    else "Your talk is today" if days == 0 else f"Talk was {-days} days ago")
    chips = f'<span class="chip">{e(when)}</span>' if when else ""
    gem = ('<span><span class="dot"></span>Gemma ready</span>' if ollama_ok
           else '<span><span class="dot off"></span>Built-in tips (Ollama is off)</span>')
    mark = '<span class="mark"><i style="height:9px"></i><i style="height:16px"></i><i style="height:24px"></i></span>'
    return (f'<div class="sl top"><div class="logo">{mark}Stage Ladder</div>'
            f'<div class="meta">{chips}{gem}<span>Private, on this laptop</span></div></div>')


_MIC = ("""<svg class="mic" viewBox="0 0 120 220" aria-hidden="true">
<circle class="ring" cx="60" cy="71" r="46" fill="none" stroke="#fff" stroke-width="2"/>
<circle class="ring" cx="60" cy="71" r="46" fill="none" stroke="#fff" stroke-width="2"/>
<circle class="ring" cx="60" cy="71" r="46" fill="none" stroke="#fff" stroke-width="2"/>
<ellipse cx="60" cy="208" rx="34" ry="7" fill="#0A2A52" opacity=".75"/><rect x="58" y="116" width="4" height="92" fill="#0A2A52" opacity=".8"/>
<rect x="46" y="106" width="28" height="12" rx="4" fill="#0A2A52" opacity=".85"/>
<rect x="40" y="26" width="40" height="84" rx="20" fill="#EAF3FC" stroke="#fff" stroke-width="2"/>
<g stroke="#0A2A52" stroke-opacity=".28" stroke-width="2" stroke-linecap="round"><line x1="47" y1="48" x2="73" y2="48"/><line x1="47" y1="60" x2="73" y2="60"/>
<line x1="47" y1="72" x2="73" y2="72"/><line x1="47" y1="84" x2="73" y2="84"/><line x1="47" y1="96" x2="73" y2="96"/></g>
<ellipse cx="52" cy="40" rx="5" ry="9" fill="#fff" opacity=".7"/></svg>""")


def _crowd(rung):
    rnd = random.Random(11)
    rim = "rgba(255,110,150,.7)" if rung == 4 else "rgba(255,255,255,.40)"
    out = []
    for n, d, bottom, op in [(20, 20, 38, .55), (12, 32, 8, .8), (8, 46, -22, .97)]:
        for i in range(n):
            left = (i + .5) / n * 100 + rnd.uniform(-2.2, 2.2)
            size = d * rnd.uniform(.88, 1.12)
            out.append(f'<div class="pp" style="left:{left:.1f}%;bottom:{bottom + rnd.randint(-4, 4)}px;opacity:{op};'
                       f'--d:{rnd.uniform(0, 3.2):.2f}s;--s:{size:.0f}px;--rim:{rim}"><i></i><b></b></div>')
    return "".join(out)


def _stage(eyebrow, title, sub, big, small, rung):
    return ('<div class="sl herobox"><div class="beam b1"></div><div class="beam b2"></div><div class="beam b3"></div>'
            '<div class="pool"></div>'
            f'<div class="row"><div><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{sub}</p></div>'
            f'<div class="stagebox">{_MIC}<div class="glass"><b>{big}</b><small>{small}</small></div></div></div>'
            f'<div class="capt">Rung {rung} &middot; {e(CAPTIONS[rung])}</div><div class="crowd">{_crowd(rung)}</div></div>')


def hero_html(runs, profile, rung=1):
    if not runs:
        who = f", {e(profile['alias'])}" if profile.get("alias") else ""
        return _stage("WELCOME", f"Ready when you are{who}",
                      "Pick a rung, press record, and give your talk out loud.", str(rung), "your rung", rung)
    r = runs[-1]
    sub = f'{r["detail"].get("duration_text", "")} &middot; {r["words"]} words'
    if len(runs) >= 2 and r["fillers_per_min"] < min(x["fillers_per_min"] for x in runs[:-1]):
        sub += " &middot; your best run yet for fillers"
    return _stage(f"RUN {r['id']}", e(r["topic"] or "Practice run"), sub,
                  f'{r["fillers_per_min"]:g}', "fillers a minute", rung)


def welcome_html(mode, alias=""):
    if mode == "lock":
        return _stage("WELCOME", "Log in to Stage Ladder",
                      "Log in to open your practice space, or create a new account.", "&#128274;", "private", 2)
    return _stage("WELCOME", "Welcome to Stage Ladder",
                  "A private place to practice your talk out loud. Setting up takes about a minute.", "1", "minute to set up", 2)


def mic_check_html(prefix):
    return (f'<div class="sl miccard"><div id="{prefix}-micmsg" class="micmsg">Press <b>Test my microphone</b>. '
            'Your browser will ask for permission with a small pop-up near the address bar. Choose <b>Allow</b>.</div>'
            f'<div class="miclevel"><i id="{prefix}-micbar"></i></div></div>')


def mic_js(prefix):
    """Asks the browser for the microphone and shows a live level meter for a few seconds."""
    return """async () => {
  const msg = document.getElementById('%(p)s-micmsg'), bar = document.getElementById('%(p)s-micbar');
  if (!msg) return;
  const say = (t, ok) => { msg.textContent = t; msg.style.color = ok === true ? 'var(--good)' : ok === false ? 'var(--pause-text)' : ''; };
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { say('This browser cannot reach the microphone. Use Chrome or Edge at http://127.0.0.1.', false); return; }
  say('Waiting for you to click Allow in the browser pop-up...');
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({audio: true}); }
  catch (err) {
    say(err.name === 'NotAllowedError' ? 'The microphone is blocked. Click the lock or microphone icon at the left of the address bar, choose Allow, then press the button again.'
        : 'No microphone was found. Plug one in or choose one in Windows sound settings.', false); return; }
  say('Say something. The bar below should move.');
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const an = ctx.createAnalyser(); an.fftSize = 512; ctx.createMediaStreamSource(stream).connect(an);
  const buf = new Uint8Array(an.fftSize); const t0 = performance.now(); let heard = false;
  const tick = () => {
    an.getByteTimeDomainData(buf); let peak = 0; for (const v of buf) peak = Math.max(peak, Math.abs(v - 128));
    const lvl = Math.min(1, peak / 64); bar.style.width = (lvl * 100) + '%%';
    if (lvl > 0.12 && !heard) { heard = true; say('I can hear you. Your microphone works.', true); }
    if (performance.now() - t0 < 8000) { requestAnimationFrame(tick); }
    else { stream.getTracks().forEach(t => t.stop()); ctx.close(); bar.style.width = '0%%';
      if (!heard) say('Connected, but I heard nothing. Speak louder, or check the right microphone is selected in Windows.', false); }
  };
  tick();
}""" % {"p": prefix}


def ladder_html(selected, unlocked, streak, goal):
    nodes = []
    for n, title, sub in RUNGS:
        if n == selected:
            cls, dot, small = "now", str(n), sub
        elif n > unlocked:
            cls, dot, small = "lock", "&#128274;", "locked"
        elif n < unlocked:
            cls, dot, small = "done", "&#10003;", "cleared"
        else:
            cls, dot, small = "", str(n), "available"
        nodes.append(f'<div class="step {cls}"><div class="circle">{dot}</div><b>{title}</b><small>{small}</small></div>')
    p = (unlocked - 1) / 3 * 100
    line = f"linear-gradient(90deg,var(--good) 0 {p:.0f}%,var(--track) {p:.0f}%)"
    if unlocked < 4:
        txt = f"Two runs in a row under {goal:g} fillers a minute unlock rung {unlocked + 1}"
        bar = f'<div class="bar"><i style="width:{streak / 2 * 100:.0f}%"></i></div><span>{streak} of 2</span>'
    else:
        txt, bar = "You have reached the top rung", ""
    return (f'<div class="sl card"><div class="steps" style="--line:{line}">{"".join(nodes)}</div>'
            f'<div class="unlock"><span>{txt}</span>{bar}</div></div>')


def transcript_html(run):
    if not run:
        return ""
    d = run["detail"]
    parts = []
    for kind, text in d["tokens"]:
        t = e(text)
        parts.append({"filler": f'<span class="f">{t}</span>', "pause": f'<span class="p">{t}</span>',
                      "strong": f'<span class="g">{t}</span>'}.get(kind, t))
    ticks = "".join(f'<i style="left:{p}%"></i>' for p in d["filler_pos"])
    ticks += "".join(f'<i class="pz" style="left:{p}%;width:{max(w, 1)}%"></i>' for p, w in d["pause_pos"])
    ax = "".join(f"<span>{a}</span>" for a in d["axis"])
    return ('<div class="sl card"><div class="lab">WHAT YOU SAID</div>'
            f'<div class="tx">{" ".join(parts)}</div>'
            '<div class="legend"><span><span class="f" style="padding:0 7px">um</span> filler words</span>'
            '<span><span class="p" style="padding:0 7px">1.5s</span> long pauses</span>'
            '<span><span class="g">sentence</span> strong moments</span></div>'
            f'<div class="tl">{ticks}</div><div class="ax">{ax}</div></div>')


def gauges_html(runs):
    if not runs:
        return ""
    r = runs[-1]
    first = runs[0]["fillers_per_min"]
    if len(runs) > 1 and r["fillers_per_min"] < first:
        tag = f'<span class="tag">&#9660; {first - r["fillers_per_min"]:g} since run {runs[0]["id"]}</span>'
    elif len(runs) == 1:
        tag = '<span class="tag warm">first run</span>'
    else:
        tag = '<span class="tag warm">keep going</span>'
    lo, hi = 60, 200
    pos = (min(max(r["wpm"], lo), hi) - lo) / (hi - lo) * 100
    band_l = (SWEET_SPOT[0] - lo) / (hi - lo) * 100
    band_w = (SWEET_SPOT[1] - SWEET_SPOT[0]) / (hi - lo) * 100
    ok = r["detail"].get("pace_note") == "in your sweet spot"
    return ('<div class="sl">'
            f'<div class="card tile" style="--bar:#F2A33A"><small>Fillers per minute</small><div class="n">{r["fillers_per_min"]:g}</div>{tag}</div>'
            f'<div class="card tile" style="--bar:var(--accent)"><small>Pace</small><div class="n">{r["wpm"]}<u>words a minute</u></div>'
            f'<div class="range"><i style="left:{band_l:.0f}%;width:{band_w:.0f}%"></i><b style="left:calc({pos:.0f}% - 3px)"></b></div>'
            f'<span class="tag{"" if ok else " warm"}">{e(r["detail"].get("pace_note", ""))}</span></div>'
            f'<div class="card tile" style="--bar:#E8588A"><small>Longest pause</small><div class="n">{r["longest_pause"]:g}<u>seconds</u></div></div></div>')


def coach_html(run):
    if not run:
        return ('<div class="sl card"><div class="lab">YOUR RESULTS</div><div class="empty">After your first run, '
                'your words appear here with every filler word and long pause highlighted, along with one kind note '
                'from your listener and a chart of your progress.<br>No microphone? You can upload a recording instead.</div></div>')
    src = {"gemma": "Written by Gemma 3 1B on this laptop",
           "fallback": "Built-in tips. Start Ollama to get notes from Gemma",
           "numbers": "Numbers only on this rung"}.get(run["coach_source"], "")
    qs = ""
    if run["questions"]:
        label = "ONE TOUGH QUESTION" if len(run["questions"]) == 1 else "TOUGH QUESTIONS"
        qs = (f'<div class="qs"><small>{label} &middot; answer out loud in your next run</small>'
              + "<br>".join(e(q) for q in run["questions"]) + "</div>")
    return ('<div class="sl card"><div class="lab">YOUR LISTENER SAYS</div><div class="coach"><div class="av">&#10022;</div>'
            f'<div><p>{e(run["feedback"])}</p><div class="src">{src}</div></div></div>{qs}</div>')


def chart_html(runs, goal):
    runs = runs[-12:]
    if not runs:
        return ""
    vals = [r["fillers_per_min"] for r in runs]
    ymax = max(max(vals), goal) * 1.25 + 1
    n = len(vals)
    xs = [60 + i * 780 / max(n - 1, 1) for i in range(n)] if n > 1 else [450]
    ys = [180 - v / ymax * 130 for v in vals]
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in zip(xs, ys))
    gy = 180 - goal / ymax * 130
    dots = ""
    for i, (x, y, v, r) in enumerate(zip(xs, ys, vals, runs)):
        last = i == n - 1
        dots += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{9 if last else 6}" style="fill:var(--stroke);stroke:var(--dot-ring);stroke-width:3"/>'
                 f'<text x="{x:.0f}" y="{y - 15:.0f}" text-anchor="middle" font-size="14" font-weight="700" style="fill:var(--text)">{v:g}</text>'
                 f'<text x="{x:.0f}" y="210" text-anchor="middle" font-size="12" style="fill:var(--muted)">run {r["id"]}</text>')
    area = f'<polygon points="{xs[0]:.0f},180 {pts} {xs[-1]:.0f},180" fill="url(#ar)"/>' if n > 1 else ""
    line = f'<polyline points="{pts}" fill="none" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" style="stroke:var(--stroke)"/>' if n > 1 else ""
    return ('<div class="sl card"><div class="lab">FILLERS PER MINUTE, RUN BY RUN</div>'
            '<svg viewBox="0 0 900 222" width="100%"><defs><linearGradient id="ar" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" style="stop-color:var(--stroke);stop-opacity:.28"/><stop offset="1" style="stop-color:var(--stroke);stop-opacity:0"/></linearGradient></defs>'
            f'<line x1="30" x2="880" y1="{gy:.0f}" y2="{gy:.0f}" stroke-dasharray="6 6" stroke-width="2" style="stroke:var(--good)"/>'
            f'<text x="34" y="{gy + 18:.0f}" font-size="12" font-weight="700" style="fill:var(--good)">your goal: under {goal:g}</text>'
            f'{area}{line}{dots}</svg></div>')


def calm_html(profile, runs):
    who = f"{e(profile['alias'])}, " if profile.get("alias") else ""
    if not runs:
        return ""
    if len(runs) == 1:
        txt = f"{who}one run down. That was the hard part."
    else:
        a, b = runs[0]["fillers_per_min"], runs[-1]["fillers_per_min"]
        trend = (f"your fillers are down from {a:g} to {b:g} a minute" if b < a
                 else f"you are holding steady at {b:g} fillers a minute")
        txt = f"<b>Before your talk:</b> {who}you have practiced {len(runs)} times, and {trend}. You have got this."
    return f'<div class="sl calm">{txt}</div>'