"""
Genera el instrumental de "De un «Veremos» a Dos Años".

Estilo: Fusión romántica de Kali Uchis «Telepatía» (dream pop latino / R&B, Rhodes,
        groove sensual suave) con MC Aese «Beso a Beso» (rap romántico íntimo,
        guitarra acústica arpegiada cálida).
Tempo: 84 BPM, 4/4, La menor / Do mayor.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, lfilter

from song_plan import BPM, BEAT, BAR, SECTIONS, TOTAL_BARS, TAIL_SECONDS

# ---------------------------------------------------------------------------
# Configuración musical
# ---------------------------------------------------------------------------

SR = 32000
PPQ = 480

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_PATH = os.path.join(OUT_DIR, "de-un-veremos-a-dos-anos.mid")
WAV_PATH = os.path.join(OUT_DIR, "de-un-veremos-a-dos-anos.wav")

SONG_SECONDS = TOTAL_BARS * BAR
TOTAL_SAMPLES = int((SONG_SECONDS + TAIL_SECONDS) * SR)

# Acordes de ensueño (Rhodes, guitarra romántica y bajo suave).
CHORDS = {
    "Am7":   {"rhodes": [57, 60, 64, 67], "guitar": [57, 60, 64, 69], "bass": 45}, # A minor 7
    "Fmaj7": {"rhodes": [53, 57, 60, 64], "guitar": [53, 57, 60, 65], "bass": 41}, # F maj 7
    "Cmaj7": {"rhodes": [55, 60, 64, 67], "guitar": [48, 55, 60, 64], "bass": 36}, # C maj 7
    "G":     {"rhodes": [55, 59, 62, 67], "guitar": [55, 59, 62, 67], "bass": 43}, # G major
    "Em7":   {"rhodes": [52, 55, 59, 62], "guitar": [52, 55, 59, 64], "bass": 40}, # E minor 7
    "Dm7":   {"rhodes": [50, 57, 60, 65], "guitar": [50, 57, 62, 65], "bass": 38}, # D minor 7
}

PROGS = {
    "intro":  ["Am7", "Fmaj7", "Cmaj7", "Em7"],
    "verse":  ["Am7", "Fmaj7", "Cmaj7", "G"],
    "verse3": ["Dm7", "Em7", "Fmaj7", "G"],
    "chorus": ["Fmaj7", "G", "Em7", "Am7"],
    "bridge": ["Fmaj7", "Em7", "Dm7", "Cmaj7"],
    "outro":  ["Am7", "Fmaj7", "Cmaj7", "Em7"],
}

# Melodía de ensueño de fondo en coros (estilo Telepatía).
HIGH_LINE = {
    "Fmaj7": [76, 81],   # E5 - A5
    "G":     [74, 79],   # D5 - G5
    "Em7":   [76, 79],   # E5 - G5
    "Am7":   [72, 76],   # C5 - E5
    "Cmaj7": [72, 79],   # C5 - G5
    "Dm7":   [74, 77],   # D5 - F5
}

SWEET_MOTIF = [69, 72, 76, 74]  # A4, C5, E5, D5 (melódico romántico)


# ---------------------------------------------------------------------------
# Eventos MIDI
# ---------------------------------------------------------------------------

@dataclass
class Note:
    start_tick: int
    dur_tick: int
    midi: int
    vel: int

    @property
    def start_seconds(self) -> float:
        return self.start_tick / PPQ * BEAT

    @property
    def dur_seconds(self) -> float:
        return self.dur_tick / PPQ * BEAT


rhodes_notes: list[Note] = []
guitar_notes: list[Note] = []
pad_notes: list[Note] = []
strings_high_notes: list[Note] = []
synth_lead_notes: list[Note] = []
bass_notes: list[Note] = []
drum_notes: list[Note] = []
perc_notes: list[Note] = []


def tick(bar: int, beat: float) -> int:
    return int(round((bar * 4.0 + beat) * PPQ))


def add_note(bucket: list[Note], bar: int, beat: float, dur_beats: float,
             midi: int, vel: int) -> None:
    bucket.append(Note(tick(bar, beat), max(1, int(round(dur_beats * PPQ))),
                       midi, vel))


def add_drum(bar: int, beat: float, midi: int, vel: int) -> None:
    add_note(drum_notes, bar, beat, 0.08, midi, vel)


def add_perc(bar: int, beat: float, midi: int, vel: int) -> None:
    add_note(perc_notes, bar, beat, 0.08, midi, vel)


for sec in SECTIONS:
    style = sec["style"]
    name = sec["name"]
    start_bar = sec["start_bar"]
    bars = sec["bars"]
    prog = PROGS[style]

    for i in range(bars):
        bar = start_bar + i
        chord_name = prog[i % len(prog)]
        ch = CHORDS[chord_name]
        r = ch["rhodes"]
        g = ch["guitar"]
        bass = ch["bass"]
        is_last = (i == bars - 1)

        # ------------------------------------------------------------------
        # 1. Rhodes Electric Piano (Cálido, trémolo suave estilo Telepatía)
        # ------------------------------------------------------------------
        if style == "intro":
            # Acordes suaves flotantes
            add_note(rhodes_notes, bar, 0.0, 3.8, r[0], 55)
            add_note(rhodes_notes, bar, 0.0, 3.8, r[1], 50)
            add_note(rhodes_notes, bar, 0.0, 3.8, r[2], 52)
            add_note(rhodes_notes, bar, 0.0, 3.8, r[3], 48)
            if i % 2 == 0:
                motif_note = SWEET_MOTIF[(i // 2) % len(SWEET_MOTIF)]
                add_note(rhodes_notes, bar, 2.0, 1.8, motif_note, 58)
        elif style in ("verse", "verse3"):
            # Chords rítmicos R&B suaves
            add_note(rhodes_notes, bar, 0.0, 1.7, r[0], 62)
            add_note(rhodes_notes, bar, 0.0, 1.7, r[1], 58)
            add_note(rhodes_notes, bar, 0.0, 1.7, r[2], 60)
            add_note(rhodes_notes, bar, 0.0, 1.7, r[3], 56)
            add_note(rhodes_notes, bar, 2.0, 1.8, r[1], 56)
            add_note(rhodes_notes, bar, 2.0, 1.8, r[3], 54)
        elif style == "chorus":
            # Exuberante y amplio estilo Telepatía
            add_note(rhodes_notes, bar, 0.0, 2.2, r[0], 72)
            add_note(rhodes_notes, bar, 0.0, 2.2, r[1], 68)
            add_note(rhodes_notes, bar, 0.0, 2.2, r[2], 70)
            add_note(rhodes_notes, bar, 0.0, 2.2, r[3], 68)
            add_note(rhodes_notes, bar, 2.5, 1.4, r[2], 65)
            add_note(rhodes_notes, bar, 2.5, 1.4, r[3] + 12, 60)
        elif style == "bridge":
            add_note(rhodes_notes, bar, 0.0, 1.8, r[0], 68)
            add_note(rhodes_notes, bar, 0.0, 1.8, r[2], 64)
            add_note(rhodes_notes, bar, 2.0, 1.8, r[1], 66)
            add_note(rhodes_notes, bar, 2.0, 1.8, r[3], 64)
        elif style == "outro":
            add_note(rhodes_notes, bar, 0.0, 3.8, r[0], 48)
            add_note(rhodes_notes, bar, 0.0, 3.8, r[2], 46)

        # ------------------------------------------------------------------
        # 2. Guitarra Acústica Romántica (Arpegio fluido estilo Beso a Beso)
        # ------------------------------------------------------------------
        if style in ("intro", "verse", "verse3", "outro"):
            # Arpegio constante de 8 notas por compás (cálido, íntimo)
            pattern = [
                (0.0, g[0], 0.45, 68),
                (0.5, g[1], 0.45, 58),
                (1.0, g[2], 0.45, 62),
                (1.5, g[3], 0.45, 65),
                (2.0, g[2], 0.45, 60),
                (2.5, g[1], 0.45, 58),
                (3.0, g[2], 0.45, 62),
                (3.5, g[3], 0.45, 64),
            ]
            for b_beat, midi_val, dur_val, vel_val in pattern:
                add_note(guitar_notes, bar, b_beat, dur_val, midi_val, vel_val)
        elif style in ("chorus", "bridge"):
            # Acompañamiento más brillante en contratiempos
            arp_chorus = [
                (0.0, g[0], 0.5, 72),
                (0.75, g[2], 0.5, 64),
                (1.5, g[3], 0.5, 66),
                (2.0, g[1], 0.5, 62),
                (2.75, g[2], 0.5, 64),
                (3.5, g[3], 0.5, 65),
            ]
            for b_beat, midi_val, dur_val, vel_val in arp_chorus:
                add_note(guitar_notes, bar, b_beat, dur_val, midi_val + 12, vel_val)

        # ------------------------------------------------------------------
        # 3. Pads de Ensueño / Synth Strings (Voz de fondo etérea)
        # ------------------------------------------------------------------
        if style in ("chorus", "bridge"):
            for idx in (r[1], r[2], r[3]):
                add_note(pad_notes, bar, 0.0, 3.9, idx + 12, 48)
        elif style == "intro" and i >= 4:
            add_note(pad_notes, bar, 0.0, 3.9, r[2] + 12, 38)
            add_note(pad_notes, bar, 0.0, 3.9, r[3] + 12, 35)

        # Melodía de cuerdas altas que flota en los coros
        if style == "chorus":
            high = HIGH_LINE.get(chord_name, [76, 81])
            add_note(strings_high_notes, bar, 0.0, 2.2, high[0], 58)
            add_note(strings_high_notes, bar, 2.0, 1.8, high[1], 54)

        # ------------------------------------------------------------------
        # 4. Sintetizador / Flauta Melódica Suave (Respuesta romántica)
        # ------------------------------------------------------------------
        if style == "verse" and i % 4 == 2:
            add_note(synth_lead_notes, bar, 2.5, 1.2, r[3] + 12, 42)
        elif style == "bridge":
            add_note(synth_lead_notes, bar, 0.0, 1.8, r[2] + 12, 48)
            add_note(synth_lead_notes, bar, 2.0, 1.8, r[3] + 12, 52)

        # ------------------------------------------------------------------
        # 5. Bajo Cálido y Redondo (Smooth Neo-Soul Bass, sin distorsión)
        # ------------------------------------------------------------------
        if style == "intro":
            if i >= 4:
                add_note(bass_notes, bar, 0.0, 3.6, bass, 65)
        elif style in ("verse", "verse3"):
            # Groove suave en 1, 2.5 y anticipación
            add_note(bass_notes, bar, 0.0, 1.6, bass, 78)
            add_note(bass_notes, bar, 2.0, 0.8, bass, 68)
            add_note(bass_notes, bar, 2.75, 1.0, bass + 7, 62)
        elif style == "chorus":
            # Groove más cadencioso estilo Telepatía
            add_note(bass_notes, bar, 0.0, 1.4, bass, 84)
            add_note(bass_notes, bar, 1.5, 0.8, bass, 72)
            add_note(bass_notes, bar, 2.5, 1.2, bass + 12, 78)
            add_note(bass_notes, bar, 3.5, 0.5, bass + 7, 70)
        elif style == "bridge":
            add_note(bass_notes, bar, 0.0, 1.8, bass, 82)
            add_note(bass_notes, bar, 2.0, 1.8, bass, 76)
        elif style == "outro":
            if i < bars - 3:
                add_note(bass_notes, bar, 0.0, 3.6, bass, 55)

        # ------------------------------------------------------------------
        # 6. Batería (Groove híbrido Telepatía x Beso a Beso)
        # ------------------------------------------------------------------
        if style == "intro":
            if i >= 6:
                # Entrada sutil de hi-hat y shaker
                for b in np.arange(0.0, 4.0, 0.5):
                    add_perc(bar, float(b), 70, 22)
            if i >= 10:
                add_drum(bar, 0.0, 36, 68)
                add_drum(bar, 2.0, 38, 55)  # rimshot suave

        elif style in ("verse", "verse3"):
            # Groove estilo Beso a Beso: íntimo, cálido, suave
            add_drum(bar, 0.0, 36, 85)       # Bombo suave
            add_drum(bar, 2.5, 36, 75)       # Bombo síncopa suave
            add_drum(bar, 1.0, 38, 78)       # Rimshot cálido (tiempo 2)
            add_drum(bar, 3.0, 38, 78)       # Rimshot cálido (tiempo 4)
            # Hi-hat y Shaker en corcheas con swing
            for b in np.arange(0.0, 4.0, 0.5):
                vel_hat = 48 if b == round(b) else 32
                add_drum(bar, float(b), 42, vel_hat)
                add_perc(bar, float(b) + 0.25, 70, 20)
            if i % 2 == 1:
                add_drum(bar, 3.5, 46, 38)   # Hi-hat abierto sutil

        elif style == "chorus":
            # Dembow lento / R&B sensual estilo Telepatía (84 BPM)
            add_drum(bar, 0.0, 36, 95)       # Bombo 1
            add_drum(bar, 2.25, 36, 82)      # Bombo dembow
            add_drum(bar, 1.0, 38, 88)       # Rimshot principal
            add_drum(bar, 1.75, 38, 68)      # Rimshot síncopa suave (Telepatía)
            add_drum(bar, 3.0, 38, 86)       # Rimshot 4
            # Hi-hat abierto sensual en contratiempos
            add_drum(bar, 1.5, 46, 45)
            add_drum(bar, 3.5, 46, 45)
            # Shakers envolventes
            for b in np.arange(0.0, 4.0, 0.25):
                add_perc(bar, float(b), 70, 28 if b % 0.5 == 0 else 18)
            # Toque de conga suave
            if i % 2 == 1:
                add_perc(bar, 2.75, 63, 38)
                add_perc(bar, 3.25, 64, 34)

        elif style == "bridge":
            for b in (0.0, 1.0, 2.0, 3.0):
                add_drum(bar, b, 36, 85 if b in (0.0, 2.0) else 72)
            add_drum(bar, 1.0, 38, 82)
            add_drum(bar, 3.0, 38, 82)
            for b in np.arange(0.0, 4.0, 0.5):
                add_drum(bar, float(b), 42, 45)

        elif style == "outro":
            if i < 6:
                add_drum(bar, 0.0, 36, 62)
                add_drum(bar, 2.0, 38, 48)
                for b in np.arange(0.0, 4.0, 1.0):
                    add_perc(bar, float(b), 70, 18)


# ---------------------------------------------------------------------------
# MIDI Builder
# ---------------------------------------------------------------------------

def vlq(n: int) -> bytes:
    if n < 0:
        raise ValueError("vlq negativo")
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def meta(kind: int, data: bytes) -> bytes:
    return bytes([0xFF, kind]) + vlq(len(data)) + data


def track_chunk(events: list[tuple[int, int, bytes]]) -> bytes:
    events.sort(key=lambda e: (e[0], e[1]))
    data = bytearray()
    last = 0
    for t, _priority, ev in events:
        data += vlq(t - last) + ev
        last = t
    data += b"\x00\xFF\x2F\x00"
    return b"MTrk" + len(data).to_bytes(4, "big") + bytes(data)


def note_events(bucket: list[Note], channel: int) -> list[tuple[int, int, bytes]]:
    events = []
    for n in bucket:
        on = bytes([0x90 | channel, n.midi, n.vel])
        off = bytes([0x80 | channel, n.midi, 0])
        events.append((n.start_tick, 1, on))
        events.append((n.start_tick + n.dur_tick, 0, off))
    return events


def build_midi() -> bytes:
    micros = int(round(60_000_000 / BPM))

    conductor = [
        (0, 0, meta(0x58, bytes([4, 2, 24, 8]))),
        (0, 0, meta(0x51, micros.to_bytes(3, "big"))),
        (0, 0, meta(0x03, b"De un Veremos a Dos Anos (Telepatia x Beso a Beso)")),
    ]
    for sec in SECTIONS:
        conductor.append((sec["start_bar"] * 4 * PPQ, 0,
                          meta(0x06, sec["name"].encode("utf-8"))))

    rhodes = [(0, 0, meta(0x03, b"Rhodes Piano")), (0, 0, bytes([0xC0, 4]))]  # Electric Piano 1
    for bar in range(TOTAL_BARS):
        rhodes.append((bar * 4 * PPQ, 0, bytes([0xB0, 64, 127])))
        rhodes.append((bar * 4 * PPQ + 4 * PPQ - 10, 0, bytes([0xB0, 64, 0])))
    rhodes += note_events(rhodes_notes, 0)

    guitar = [(0, 0, meta(0x03, b"Guitarra Acustica")), (0, 0, bytes([0xC3, 24]))] # Nylon Guitar
    guitar += note_events(guitar_notes, 3)

    pads = [(0, 0, meta(0x03, b"Dream Pad")), (0, 0, bytes([0xC4, 89]))] # Warm Pad
    pads += note_events(pad_notes, 4)

    strings_high = [(0, 0, meta(0x03, b"Cuerdas Agudas")), (0, 0, bytes([0xC5, 48]))]
    strings_high += note_events(strings_high_notes, 5)

    synth_lead = [(0, 0, meta(0x03, b"Sinte Melodico")), (0, 0, bytes([0xC6, 80]))]
    synth_lead += note_events(synth_lead_notes, 6)

    bass = [(0, 0, meta(0x03, b"Bajo Smooth")), (0, 0, bytes([0xC1, 33]))] # Fingered Bass
    bass += note_events(bass_notes, 1)

    drums = [(0, 0, meta(0x03, b"Bateria"))]
    drums += note_events(drum_notes + perc_notes, 9)

    tracks = [track_chunk(t) for t in (
        conductor, rhodes, guitar, pads, strings_high,
        synth_lead, bass, drums,
    )]
    header = b"MThd" + (6).to_bytes(4, "big") + (1).to_bytes(2, "big")
    header += len(tracks).to_bytes(2, "big") + PPQ.to_bytes(2, "big")
    return header + b"".join(tracks)


# ---------------------------------------------------------------------------
# Síntesis de Audio (WAV)
# ---------------------------------------------------------------------------

def midi_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def fade_tail(sig: np.ndarray, seconds: float = 0.02) -> np.ndarray:
    n = min(len(sig), int(seconds * SR))
    if n > 0:
        sig[-n:] *= np.linspace(1.0, 0.0, n)
    return sig


def synth_rhodes(freq: float, dur: float, vel: float) -> np.ndarray:
    """Piano eléctrico Rhodes cálido con ataque tine acampanado y trémolo suave."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    # Fundamental pura + armónicos cálidos de tine
    sig = 1.0 * np.sin(2 * math.pi * freq * t)
    sig += 0.28 * np.sin(2 * math.pi * freq * 2 * t) * np.exp(-t / 0.5)
    sig += 0.09 * np.sin(2 * math.pi * freq * 3 * t) * np.exp(-t / 0.25)
    # Tine bell click sutil
    tine_f = min(4000.0, freq * 6.5)
    sig += 0.14 * np.sin(2 * math.pi * tine_f * t) * np.exp(-t / 0.025)
    # Chorus / vibrato suave
    vib = 1.0 + 0.0025 * np.sin(2 * math.pi * 3.8 * t)
    sig *= vib
    # Envolvente decaimiento cálido
    decay = 1.4 + 75.0 / max(freq, 50.0)
    env = np.minimum(t / 0.005, 1.0) * np.exp(-t / decay)
    sig = np.tanh(sig * 1.15) * env * (0.24 * vel / 100.0)
    return fade_tail(sig)


def synth_guitar(freq: float, dur: float, vel: float) -> np.ndarray:
    """Guitarra acústica/nylon arpegiada estilo Beso a Beso."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for h, a, d in ((1, 1.0, 0.95), (2, 0.48, 0.65), (3, 0.26, 0.42),
                    (4, 0.12, 0.28), (5, 0.06, 0.19)):
        sig += a * np.sin(2 * math.pi * freq * h * t) * np.exp(-t / d)
    # Filtro cálido para guitarra de cuerdas de nylon
    b, a = butter(2, 3400.0, btype="low", fs=SR)
    sig = lfilter(b, a, sig)
    env = np.minimum(t / 0.004, 1.0)
    sig *= env * (0.20 * vel / 100.0)
    return fade_tail(sig)


def synth_pad(freq: float, dur: float, vel: float) -> np.ndarray:
    """Pad celestial de ensueño con chorus y ataque lento estilo Telepatía."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    vib = 1.0 + 0.003 * np.sin(2 * math.pi * 4.5 * t)
    sig = np.zeros(n)
    for detune in (0.997, 1.0, 1.003):
        f = freq * detune * vib
        phase = 2 * math.pi * f * t
        for h in range(1, 5):
            sig += (1.0 / h) * np.sin(h * phase + 0.2 * h)
    b, a = butter(2, 1600.0, btype="low", fs=SR)
    sig = lfilter(b, a, sig)
    attack = min(0.45, dur * 0.3)
    release = min(0.45, dur * 0.25)
    env = np.minimum(t / max(attack, 1e-4), 1.0) * np.minimum((dur - t) / max(release, 1e-4), 1.0)
    sig *= np.clip(env, 0.0, 1.0)
    peak = float(np.max(np.abs(sig)))
    if peak > 0:
        sig = sig / peak * (0.10 * vel / 100.0)
    return fade_tail(sig)


def synth_strings_high(freq: float, dur: float, vel: float) -> np.ndarray:
    """Cuerdas agudas brillantes con reverb sutil."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    vib = 1.0 + 0.0035 * np.sin(2 * math.pi * 5.2 * t + 0.3)
    sig = np.zeros(n)
    for detune in (0.998, 1.002):
        f = freq * detune * vib
        phase = 2 * math.pi * f * t
        for h in range(1, 6):
            sig += (1.0 / h) * np.sin(h * phase)
    b, a = butter(2, 4200.0, btype="low", fs=SR)
    sig = lfilter(b, a, sig)
    attack = min(0.3, dur * 0.2)
    release = min(0.35, dur * 0.25)
    env = np.minimum(t / max(attack, 1e-4), 1.0) * np.minimum((dur - t) / max(release, 1e-4), 1.0)
    sig *= np.clip(env, 0.0, 1.0)
    peak = float(np.max(np.abs(sig)))
    if peak > 0:
        sig = sig / peak * (0.09 * vel / 100.0)
    return fade_tail(sig)


def synth_lead(freq: float, dur: float, vel: float) -> np.ndarray:
    """Lead suave estilo flauta/sinte analógico vintage."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    f = freq * (1.0 + 0.002 * np.sin(2 * math.pi * 5.0 * t))
    sig = np.sin(2 * math.pi * f * t) + 0.3 * np.sin(4 * math.pi * f * t)
    b, a = butter(2, 2200.0, btype="low", fs=SR)
    sig = lfilter(b, a, sig)
    env = np.minimum(t / 0.03, 1.0) * np.exp(-t / max(0.4, dur * 1.1))
    peak = float(np.max(np.abs(sig)))
    if peak > 0:
        sig = sig / peak * (0.12 * vel / 100.0)
    return fade_tail(sig)


def synth_smooth_bass(freq: float, dur: float, vel: float) -> np.ndarray:
    """Bajo eléctrico redondo y cálido neo-soul (sin distorsión 808)."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    # Fundamental profunda + segundo armónico cálido
    sig = np.sin(2 * math.pi * freq * t) + 0.38 * np.sin(4 * math.pi * freq * t)
    sig += 0.08 * np.sin(6 * math.pi * freq * t)
    b, a = butter(2, 380.0, btype="low", fs=SR)
    sig = lfilter(b, a, sig)
    env = np.minimum(t / 0.008, 1.0) * np.exp(-t / max(0.6, dur * 1.3))
    sig = np.tanh(sig * 1.2) * env * (0.24 * vel / 100.0)
    return fade_tail(sig, 0.04)


def make_warm_kick() -> np.ndarray:
    """Bombo cálido y redondo de hip hop / R&B."""
    dur = 0.42
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 46.0 + 110.0 * np.exp(-t / 0.035)
    phase = 2 * math.pi * np.cumsum(f) / SR
    env = np.exp(-t / 0.16)
    click = np.random.randn(n) * np.exp(-t / 0.004) * 0.12
    sig = np.sin(phase) * env + click
    sig = np.tanh(sig * 1.2)
    sig /= max(1e-9, np.max(np.abs(sig)))
    return sig * 0.76


def make_rimshot() -> np.ndarray:
    """Rimshot de madera con resonancia cálida y reverb sutil estilo Telepatía."""
    dur = 0.14
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * math.pi * 1180.0 * t) * np.exp(-t / 0.026)
    body += 0.4 * np.sin(2 * math.pi * 750.0 * t) * np.exp(-t / 0.035)
    noise = np.random.randn(n) * np.exp(-t / 0.016)
    b, a = butter(2, [800.0, 5000.0], btype="band", fs=SR)
    noise = lfilter(b, a, noise) * 0.38
    sig = body + noise
    sig /= max(1e-9, np.max(np.abs(sig)))
    return sig * 0.62


def make_hat(open_hat: bool = False) -> np.ndarray:
    dur = 0.24 if open_hat else 0.07
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    hp = np.diff(np.diff(noise, prepend=0.0), prepend=0.0)
    env = np.exp(-t / (0.10 if open_hat else 0.020))
    sig = hp * env
    sig /= max(1e-9, np.max(np.abs(sig)))
    return sig * (0.20 if open_hat else 0.14)


def make_shaker() -> np.ndarray:
    dur = 0.055
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    b, a = butter(2, 5400.0, btype="high", fs=SR)
    sig = lfilter(b, a, noise) * np.exp(-t / 0.014)
    sig /= max(1e-9, np.max(np.abs(sig)))
    return sig * 0.22


def make_conga(freq: float) -> np.ndarray:
    dur = 0.20
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1.0 + 0.15 * np.exp(-t / 0.02))
    phase = 2 * math.pi * np.cumsum(f) / SR
    env = np.exp(-t / 0.08)
    sig = np.sin(phase) * env
    sig /= max(1e-9, np.max(np.abs(sig)))
    return sig * 0.32


def make_reverb_ir(dur: float = 2.4) -> np.ndarray:
    """Impulso de reverb amplio y sedoso estilo Dream Pop."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    b, a = butter(2, 4500.0, btype="low", fs=SR)
    ir = lfilter(b, a, noise) * np.exp(-t / 0.65)
    ir /= max(1e-9, np.sqrt(np.sum(ir * ir)))
    return ir


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render() -> None:
    rhodes_bus = np.zeros(TOTAL_SAMPLES)
    guitar_bus = np.zeros(TOTAL_SAMPLES)
    pad_bus = np.zeros(TOTAL_SAMPLES)
    strings_high_bus = np.zeros(TOTAL_SAMPLES)
    synth_lead_bus = np.zeros(TOTAL_SAMPLES)
    bass_bus = np.zeros(TOTAL_SAMPLES)
    drum_bus = np.zeros(TOTAL_SAMPLES)
    perc_bus = np.zeros(TOTAL_SAMPLES)

    one_shots = {
        36: make_warm_kick(),
        38: make_rimshot(),
        42: make_hat(False),
        46: make_hat(True),
        63: make_conga(220.0),
        64: make_conga(180.0),
        70: make_shaker(),
    }

    def place(bus: np.ndarray, sig: np.ndarray, start: int) -> None:
        if start >= TOTAL_SAMPLES:
            return
        end = min(TOTAL_SAMPLES, start + len(sig))
        bus[start:end] += sig[: end - start]

    for n in rhodes_notes:
        place(rhodes_bus, synth_rhodes(midi_freq(n.midi), n.dur_seconds, n.vel),
              int(n.start_seconds * SR))

    for n in guitar_notes:
        place(guitar_bus, synth_guitar(midi_freq(n.midi), n.dur_seconds, n.vel),
              int(n.start_seconds * SR))

    for n in pad_notes:
        place(pad_bus, synth_pad(midi_freq(n.midi), n.dur_seconds, n.vel),
              int(n.start_seconds * SR))

    for n in strings_high_notes:
        place(strings_high_bus,
              synth_strings_high(midi_freq(n.midi), n.dur_seconds, n.vel),
              int(n.start_seconds * SR))

    for n in synth_lead_notes:
        place(synth_lead_bus, synth_lead(midi_freq(n.midi), n.dur_seconds, n.vel),
              int(n.start_seconds * SR))

    for n in bass_notes:
        place(bass_bus, synth_smooth_bass(midi_freq(n.midi), n.dur_seconds, n.vel),
              int(n.start_seconds * SR))

    for n in drum_notes:
        place(drum_bus, one_shots[n.midi] * (n.vel / 100.0),
              int(n.start_seconds * SR))

    for n in perc_notes:
        place(perc_bus, one_shots[n.midi] * (n.vel / 100.0),
              int(n.start_seconds * SR))

    # Reverb amplio dream pop para Rhodes, guitarra, pad y cuerdas
    ir = make_reverb_ir()
    wet_source = (
        rhodes_bus * 0.65
        + guitar_bus * 0.50
        + pad_bus * 0.90
        + strings_high_bus * 0.85
        + synth_lead_bus * 0.60
    )
    wet = fftconvolve(wet_source, ir, mode="full")[:TOTAL_SAMPLES]

    # Mezcla equilibrada: cálida, envolvente y lista para voz principal
    mix = (
        rhodes_bus * 0.95
        + guitar_bus * 0.90
        + pad_bus * 0.75
        + strings_high_bus * 0.70
        + synth_lead_bus * 0.65
        + bass_bus * 0.95
        + drum_bus * 0.92
        + perc_bus * 0.65
        + wet * 0.28
    )

    # Limpieza de subgraves
    b, a = butter(2, 28.0, btype="high", fs=SR)
    mix = lfilter(b, a, mix).astype(np.float64)

    # Brillo sedoso y medios cálidos (sonido Kali Uchis / MC Aese)
    b, a = butter(2, [1800.0, 6000.0], btype="band", fs=SR)
    mix = mix + lfilter(b, a, mix).astype(np.float64) * 0.35
    b, a = butter(2, 8000.0, btype="high", fs=SR)
    mix = mix + lfilter(b, a, mix).astype(np.float64) * 0.18

    # Pegada suave analógica y normalización
    mix = np.tanh(mix * 1.35)
    peak = float(np.max(np.abs(mix)))
    if peak > 0:
        mix = mix / peak * 0.95

    fade_in = int(0.8 * SR)
    fade_out = int(4.5 * SR)
    mix[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    mix[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)

    audio = np.int16(np.clip(mix, -1.0, 1.0) * 32767)
    wavfile.write(WAV_PATH, SR, audio)

    print(f"WAV: {WAV_PATH}")
    print(f"     {len(audio) / SR:.1f} s, {os.path.getsize(WAV_PATH) / 1e6:.1f} MB")


def main() -> None:
    midi = build_midi()
    with open(MIDI_PATH, "wb") as f:
        f.write(midi)
    print(f"MIDI: {MIDI_PATH}")
    print(f"      {len(midi) / 1024:.1f} KB, {TOTAL_BARS} compases, {BPM} BPM")
    render()


if __name__ == "__main__":
    main()
