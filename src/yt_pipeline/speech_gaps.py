"""Trim sustained low-energy gaps before measuring and aligning narration."""
from array import array
from pathlib import Path
from uuid import uuid4
import wave

from .core import Held, digest, file_hash


def tighten_quiet_pcm(samples, rate):
    """Keep consonants, breaths and short pauses; cut the center of long rests."""
    length = len(samples)
    threshold = max(32, round(max(map(abs, samples), default=0) * .008))
    window = max(1, round(rate * .008))
    cuts = []

    def cut_gap(start, end):
        if start == 0:
            cuts.append((0, max(0, end - round(rate * .024))))
        elif end == length:
            cuts.append((min(end, start + round(rate * .040)), end))
        elif end - start >= round(rate * .176):
            keep = round(rate * .060)
            cuts.append((start + keep, end - keep))

    quiet_start = None
    has_speech = False
    for start in range(0, length, window):
        block = samples[start:start + window]
        if max(map(abs, block)) <= threshold:
            if quiet_start is None:
                quiet_start = start
        else:
            has_speech = True
            if quiet_start is not None:
                cut_gap(quiet_start, start)
                quiet_start = None
    if not has_speech:
        return samples
    if quiet_start is not None:
        cut_gap(quiet_start, length)

    result = array("h")
    cursor = 0
    for start, stop in cuts:
        if start < stop:
            result.extend(samples[cursor:start])
            cursor = stop
    result.extend(samples[cursor:])
    return result


def tighten_speech_file(path, cache):
    path = Path(path)
    target = Path(cache) / (digest(["tight-quiet-speech-v1", file_hash(path)]) + ".wav")
    with wave.open(str(path), "rb") as source:
        if source.getnchannels() != 1 or source.getsampwidth() != 2:
            raise Held("voice_channels", "Tight narration needs mono 16-bit PCM.")
        rate = source.getframerate()
        original_count = source.getnframes()
        if not target.is_file():
            original = array("h")
            original.frombytes(source.readframes(original_count))
            tight = tighten_quiet_pcm(original, rate)
            if len(tight) == original_count:
                return path, 0
            temp = target.with_name(target.stem + "." + uuid4().hex + ".partial.wav")
            with wave.open(str(temp), "wb") as output:
                output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
                output.writeframes(tight.tobytes())
            temp.replace(target)
    with wave.open(str(target), "rb") as final:
        removed_ms = round(1000 * (original_count - final.getnframes()) / rate)
    return target, removed_ms
