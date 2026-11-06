from array import array
import math
import wave

from yt_pipeline.speech_gaps import tighten_quiet_pcm, tighten_speech_file


def tone(seconds, rate=24000, gain=5000):
    return array("h", (round(gain * math.sin(2 * math.pi * 220 * i / rate))
                       for i in range(round(seconds * rate))))


def test_tight_speech_preserves_quiet_consonants_and_speech_samples():
    rate = 24000
    before, consonant, after = tone(.24), tone(.04, gain=300), tone(.32)
    original = (array("h", [0]) * 4800 + before + array("h", [0]) * 1920 + consonant
                + array("h", [0]) * 9600 + after + array("h", [0]) * 6000)
    tight = tighten_quiet_pcm(original, rate)
    assert len(tight) < len(original) - rate * .5
    # Every nonzero sample remains intact and ordered, including the quiet voice.
    assert [v for v in tight if v] == [v for v in original if v]
    assert len(tighten_quiet_pcm(array("h", [0]) * 5000, rate)) == 5000


def test_trimmed_wav_cache_keeps_original_and_records_removed_time(tmp_path):
    rate = 24000
    path = tmp_path / "original.wav"
    samples = array("h", [0]) * 4800 + tone(.3) + array("h", [0]) * 7200
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        output.writeframes(samples.tobytes())
    original_bytes = path.read_bytes()
    trimmed, removed_ms = tighten_speech_file(path, tmp_path)
    assert 400 < removed_ms < 500
    assert path.read_bytes() == original_bytes
    assert tighten_speech_file(path, tmp_path) == (trimmed, removed_ms)
