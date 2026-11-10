"""Compara bandas finas por sección para revisar el contraste dramático."""

import numpy as np
from scipy.io import wavfile
from scipy.signal import welch

import song_plan as sp

sr, x = wavfile.read("de-un-veremos-a-dos-anos.wav")
y = x.astype(np.float32) / 32768.0

print(f"{'Sección':14} {'rms':>5} {'sub':>5} {'bajo':>5} {'medios':>6} "
      f"{'pres':>5} {'aire':>5}")
for s in sp.SECTIONS:
    a = int(s["start"] * sr)
    b = int(s["end"] * sr)
    seg = y[a:b]
    ff, pp = welch(seg, fs=sr, nperseg=8192)

    def bb(lo, hi):
        m = (ff >= lo) & (ff < hi)
        return float(np.sum(pp[m]) / np.sum(pp))

    print(f"{s['name']:14} {np.sqrt(np.mean(seg * seg)):5.3f} "
          f"{bb(20, 80):5.2f} {bb(80, 250):5.2f} {bb(250, 1200):6.2f} "
          f"{bb(1200, 4000):5.3f} {bb(4000, 12000):5.3f}")
