"""
Crea dos pistas auxiliares para grabar la voz:

  - de-un-veremos-a-dos-anos-guia.wav  (1 compás de conteo + instrumental)
  - de-un-veremos-a-dos-anos-click.wav (1 compás de conteo + clic)

La canción original empieza en 0:00; en la guía empieza en 0:03.3
(después de 4 clics).
"""

from __future__ import annotations

import math
import os

import numpy as np
from scipy.io import wavfile

from song_plan import BAR, BEAT

SR = 32000

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(OUT_DIR, "de-un-veremos-a-dos-anos.wav")
GUIDE = os.path.join(OUT_DIR, "de-un-veremos-a-dos-anos-guia.wav")
CLICK = os.path.join(OUT_DIR, "de-un-veremos-a-dos-anos-click.wav")


def click(accent: bool = False) -> np.ndarray:
    dur = 0.09
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 1650.0 if accent else 1150.0
    env = np.exp(-t / 0.014)
    sig = np.sin(2 * math.pi * freq * t) * env
    sig += 0.08 * np.random.randn(n) * np.exp(-t / 0.004)
    sig /= max(1e-9, np.max(np.abs(sig)))
    return sig.astype(np.float32) * (0.55 if accent else 0.38)


def mix_at(dst: np.ndarray, src: np.ndarray, start: int) -> None:
    end = min(len(dst), start + len(src))
    if end > start:
        dst[start:end] += src[: end - start]


def main() -> None:
    _, raw = wavfile.read(BASE)
    base = raw.astype(np.float32) / 32768.0

    count_in = int(round(BAR * SR))
    total = count_in + len(base)
    guide = np.zeros(total, dtype=np.float32)
    metro = np.zeros(total, dtype=np.float32)

    # Conteo: 4 clics, el primero acentuado.
    for beat in range(4):
        mix_at(guide, click(beat == 0), int(round(beat * BEAT * SR)))
        mix_at(metro, click(beat == 0), int(round(beat * BEAT * SR)))

    # Metrónomo de la canción: clic suave en cada tiempo.
    total_beats = int(math.ceil(len(base) / (BEAT * SR)))
    for beat in range(total_beats):
        start = count_in + int(round(beat * BEAT * SR))
        mix_at(metro, click(beat % 4 == 0) * 0.55, start)

    # Guía = conteo + instrumental.
    guide[count_in:count_in + len(base)] += base

    def save(path: str, data: np.ndarray) -> None:
        peak = float(np.max(np.abs(data)))
        if peak > 0:
            data = data / peak * 0.95
        wavfile.write(path, SR, np.int16(np.clip(data, -1.0, 1.0) * 32767))
        print(f"{os.path.basename(path)}: {len(data) / SR:.1f} s")

    save(GUIDE, guide)
    save(CLICK, metro)


if __name__ == "__main__":
    main()
