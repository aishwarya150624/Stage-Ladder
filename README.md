# Stage Ladder

A private, offline speaking coach for anyone who dreads speaking in public.
You practice your talk out loud on your laptop. The app measures your pace, filler words and
pauses with plain code, adds one kind note from a small local AI model, saves every run, and
lets you climb a four-rung ladder from practicing alone to facing a skeptical room.

Built for the Hacktoberfest Weekend Challenge: Build for a Friend.

## What is open, and where it runs

| Piece | What it does | File |
|---|---|---|
| faster-whisper (Whisper `base`) | speech to text with word timestamps, on the CPU | `transcribe.py` |
| Gemma 3 1B through Ollama | writes the kind note and the tough questions | `coach.py` |
| Plain Python | pace, fillers per minute, pauses (no AI, so the numbers can be trusted) | `metrics.py` |
| SQLite | every run and your profile, in one local file | `db.py` |
| Gradio | the interface | `app.py`, `ui.py` |

Your recordings and results stay on your laptop. The recording is deleted after it is transcribed.
Gradio telemetry is switched off. The interface has animated spotlights, a microphone and an audience that reacts to your rung (animations stop if your system asks for reduced motion). The only internet use is the one-time model downloads.
If Ollama is not running, the app falls back to built-in tips instead of Gemma notes and says so on screen.

## Run it (Windows, VS Code terminal)

```
ollama pull gemma3:1b
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Switch the look (PowerShell):  `$env:STAGE_THEME="ocean"; python app.py`   (Command Prompt: `set STAGE_THEME=ocean`)

The first real run downloads the Whisper model once (around 150 MB), so give it a minute.

## How to use it

1. Create an account (or log in), then open Your profile to change your name, talk date, filler goal and tone.
2. Pick a rung, press the microphone, give your talk, press Analyze my run.
3. Read the highlighted transcript, the dials, the note, and the chart.
4. Two runs in a row under your goal unlock the next rung.
5. No microphone? Upload a recording instead.

## Accounts, login and microphone

- **Anyone can use it:** the first screen has two tabs, Log in and Create account. Any number of people can sign up (username + password, 4 or more characters) and log in again as many times as they like.
- **Separate data:** every account has its own profile, runs, ladder progress and chart. Nobody sees another account's practice.
- **Log out:** the Log out button inside the app returns to the login screen (and clears the topic and recording box for the next person).
- **Change password / delete account:** both are inside the app, under Your profile and Delete my account. Deleting removes only that account.
- **Forgot your password?** It cannot be recovered, because nothing is stored in the cloud. Create a new account with another username.
- **Upgrading from the single-user version:** your old profile and runs are kept as an account named after your old name (lowercase, for example `priya`). If you had a PIN, it is now that account's password. If you had none, log in with the username and an empty password, then set one under Your profile.
- **Microphone:** the permission pop-up belongs to your browser (Chrome or Edge), not the app. The Test my microphone button asks for it at a friendly moment and shows a live level meter. If you pressed Block, click the lock or microphone icon in the address bar, choose Allow, and test again.
- **Honest limit:** passwords are salted and hashed, but this is a privacy screen for a shared laptop, not encryption. The database file is not encrypted, and the app only listens on this laptop (127.0.0.1).

## Settings (optional environment variables)

`STAGE_MODEL` (default `gemma3:1b`), `STAGE_WHISPER` (default `base`, try `small` if "um" and "uh" are missing),
`STAGE_LANG` (for example `en`), `STAGE_THEME` (`ocean` by default, or `sunset` or `dusk`).

## Honest limits

- This is practice support, not therapy. If fear of speaking is stopping someone from doing things they need to do, a counselor can help.
- Whisper can leave "um" and "uh" out of transcripts. Test with a recording that has deliberate fillers.
- A 1B model can sound generic, and "things never to say" is only a prompt instruction plus a text check, so it can miss.
- Filler counts depend on the transcript, so treat them as a trend, not an exact score.

## License

MIT. See LICENSE.
