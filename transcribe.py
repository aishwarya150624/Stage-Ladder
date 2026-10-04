"""Speech to text with faster-whisper, running on the CPU. Word timestamps feed the metrics."""
import os
import wave
from functools import lru_cache

MODEL_SIZE = os.environ.get("STAGE_WHISPER", "base")
LANGUAGE = os.environ.get("STAGE_LANG") or None
# A filler-style prompt nudges Whisper to keep "um" and "uh" instead of cleaning them out.
PROMPT = "Umm, let me think, like, hmm... okay, so, you know, uh, basically..."
RATE = 16000


@lru_cache(maxsize=1)
def _model():
    from faster_whisper import WhisperModel

    try:  # fully offline once the model is cached
        return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", local_files_only=True)
    except Exception:  # first run: download the model once
        return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")


def _resample(audio, rate):
    import numpy as np

    if rate == RATE or len(audio) == 0:
        return audio.astype(np.float32)
    n = int(len(audio) * RATE / rate)
    return np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio).astype(np.float32)


def _load_wav(path):
    """Plain 16-bit WAV (what the microphone box records) read with the standard library: no decoder needed."""
    import numpy as np

    with wave.open(path, "rb") as w:
        channels, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        if width != 2:
            raise ValueError("not 16-bit PCM")
        data = np.frombuffer(w.readframes(frames), dtype=np.int16)
    if channels > 1:
        data = data[: len(data) // channels * channels].reshape(-1, channels).mean(axis=1)
    return _resample(data.astype(np.float32) / 32768.0, rate)


def _as_list(x):
    return [] if x is None else (x if isinstance(x, list) else [x])


def _load_av(path):
    """Any other format (mp3, m4a, webm...) through PyAV, called the simple way so old and new versions both work."""
    import av
    import numpy as np

    resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=RATE)
    chunks = []
    with av.open(path) as container:
        stream = next(s for s in container.streams if s.type == "audio")
        for frame in container.decode(stream):
            for out in _as_list(resampler.resample(frame)):
                chunks.append(out.to_ndarray().reshape(-1))
        for out in _as_list(resampler.resample(None)):  # flush what is left
            chunks.append(out.to_ndarray().reshape(-1))
    if not chunks:
        raise ValueError("no audio found")
    return np.concatenate(chunks).astype(np.float32) / 32768.0


def _load_audio(path):
    """Decode the recording ourselves. This avoids faster-whisper's own decoder call, which breaks
    with some av versions ("unexpected keyword argument 'metadata_errors'")."""
    try:
        return _load_wav(path)
    except Exception:
        return _load_av(path)


def transcribe(path):
    try:
        audio = _load_audio(path)
    except Exception:
        audio = path  # last resort: let faster-whisper try to read the file itself
    segments, _ = _model().transcribe(
        audio, language=LANGUAGE, word_timestamps=True, initial_prompt=PROMPT,
        vad_filter=False, condition_on_previous_text=False, beam_size=5,
    )
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"text": w.word.strip(), "start": w.start, "end": w.end})
    return words