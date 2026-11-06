"""Per-beat timing for source Shorts and pronunciation of connected names."""
from array import array
from pathlib import Path
import re
import wave

from .core import Held
from .speech_delivery import number


def delivery_for(unit, request, default_pause, *, tight_default=False):
    config = request.get("source_delivery", {})
    if not isinstance(config, dict):
        raise Held("speech_delivery", "Supply a source delivery object.")
    tight = config.get("tight_speech", tight_default)
    if type(tight) is not bool:
        raise Held("speech_delivery", "Tight speech must be true or false.")
    if not config and not tight:
        return {"pause_after": default_pause}
    phrases = config.get("linked_phrases", [])
    pauses = config.get("pauses_after", {})
    if not isinstance(phrases, list) or len(phrases) > 12 or any(
        not isinstance(phrase, str) or not 2 <= len(phrase.split()) <= 8 or len(phrase) > 80
        for phrase in phrases
    ):
        raise Held("speech_delivery", "Use short exact phrases for connected speech.")
    if not isinstance(pauses, dict):
        raise Held("speech_delivery", "Supply a map from beat IDs to pause lengths.")
    return {
        "pause_after": number(pauses.get(unit["id"], config.get("pause_after", default_pause)), 0, .9),
        **({"tight_speech": True} if tight else {}),
        "linked_phrases": [p for p in phrases if p.casefold() in unit["text"].casefold()],
        "speech_segments": [{
            "text": unit["text"],
            "speed": number(config.get("speed", 1.10 if tight else 1), .9, 1.15),
            "pause_after": 0,
        }],
    }


def connected_text(text, phrases):
    """Remove punctuation inside named phrases in the speech engine's input."""
    for phrase in phrases:
        text = re.sub(
            re.escape(phrase),
            lambda match: re.sub(r"[:,;]", "", match.group()),
            text,
            flags=re.IGNORECASE,
        )
    return text


def add_source_cues(workspace, timing, cues, folder):
    from .sound_library import install_sound_library, mix_sound_events
    if not isinstance(cues, dict) or len(cues) > 8 or set(cues) - {u["id"] for u in timing["units"]}:
        raise Held("sound_events", "Choose up to eight actual beats for sound cues.")
    events = []
    for unit in timing["units"]:
        category = cues.get(unit["id"])
        if category is None:
            continue
        if category not in ("transition", "reveal", "impact"):
            raise Held("sound_events", "Choose transition, reveal, or impact.")
        events.append({"category": category, "start": unit["start"] + .08, "gain": .48})
    install_sound_library(workspace, include_ambience=False)
    with wave.open(timing["audio"], "rb") as original:
        if original.getnchannels() != 1 or original.getsampwidth() != 2:
            raise Held("sound_events", "The source narration must use mono 16-bit PCM.")
        rate = original.getframerate()
        samples = array("h")
        samples.frombytes(original.readframes(original.getnframes()))
    mixed = mix_sound_events(workspace, samples, rate, events)
    path = Path(folder) / "narration-with-cues.wav"
    temporary = path.with_suffix(".partial.wav")
    with wave.open(str(temporary), "wb") as output:
        output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        output.writeframes(samples.tobytes())
    temporary.replace(path)
    return {**timing, "audio": str(path), "effects": mixed["effects"]}
