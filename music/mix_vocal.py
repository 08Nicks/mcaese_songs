"""
Mezcla tu voz con la instrumental.

Uso típico (grabaste con la pista guía):
    python music/mix_vocal.py music/voz/voz-principal.wav

La pista guía tiene 1 compás de conteo (2.5 s a 96 BPM), así que por
defecto se recortan esos 2.5 s del inicio de tu grabación.

Si grabaste sobre la instrumental limpia (sin conteo):
    python music/mix_vocal.py music/voz/voz-principal.wav --trim 0

Si grabaste solo una sección:
    python music/mix_vocal.py music/voz/coro.wav --trim 0 --place 87.5
    (87.5 s = donde empieza el Coro 1 en la canción)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile

import imageio_ffmpeg
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, lfilter

from song_plan import BAR

SR = 32000
HERE = os.path.dirname(os.path.abspath(__file__))
INSTRUMENTAL = os.path.join(HERE, "de-un-veremos-a-dos-anos.wav")
DEFAULT_OUT = os.path.join(HERE, "de-un-veremos-a-dos-anos-mezcla.wav")

# Escala de La menor / Do mayor: C, D, E, F, G, A, B
SCALE_NOTES = [0, 2, 4, 5, 7, 9, 11]


def snap_midi_to_scale(midi_val: float) -> float:
    semitone = int(round(midi_val))
    pc = semitone % 12
    best_pc = min(SCALE_NOTES, key=lambda note: min(abs(pc - note), 12 - abs(pc - note)))
    diff = (best_pc - pc + 6) % 12 - 6
    return float(semitone + diff)


def pitch_shift_vocoder(x: np.ndarray, shift_semitones: float, sr: int = SR) -> np.ndarray:
    if abs(shift_semitones) < 0.05:
        return x
    factor = 2.0 ** (shift_semitones / 12.0)
    nperseg = 1024
    hop = nperseg // 4
    f, t, Zxx = signal.stft(x, fs=sr, nperseg=nperseg, noverlap=nperseg - hop)
    new_len = int(len(t) / factor)
    if new_len < 2:
        return x
    old_indices = np.linspace(0, len(t) - 1, new_len)
    phase_advance = 2 * np.pi * hop * np.arange(len(f)) / nperseg
    Z_stretched = np.zeros((len(f), new_len), dtype=complex)
    phase = np.angle(Zxx[:, 0])
    Z_stretched[:, 0] = np.abs(Zxx[:, 0]) * np.exp(1j * phase)
    for i in range(1, new_len):
        idx = old_indices[i]
        i0 = int(idx)
        i1 = min(len(t) - 1, i0 + 1)
        frac = idx - i0
        mag = (1 - frac) * np.abs(Zxx[:, i0]) + frac * np.abs(Zxx[:, i1])
        dphase = np.angle(Zxx[:, i1]) - np.angle(Zxx[:, i0]) - phase_advance
        dphase = (dphase + np.pi) % (2 * np.pi) - np.pi
        phase += (phase_advance + dphase) * factor
        Z_stretched[:, i] = mag * np.exp(1j * phase)
    _, stretched = signal.istft(Z_stretched, fs=sr, nperseg=nperseg, noverlap=nperseg - hop)
    return signal.resample(stretched, len(x)).astype(np.float32)


def autotune_vocal(x: np.ndarray, strength: float = 0.80, sr: int = SR) -> np.ndarray:
    """Afinación suave de la voz a la escala de La menor / Do mayor."""
    if strength <= 0.0 or len(x) == 0:
        return x

    hop = int(0.04 * sr)
    win_len = int(0.08 * sr)
    if len(x) < win_len:
        return x

    out = np.zeros_like(x)
    norm = np.zeros_like(x)
    window = np.hanning(win_len).astype(np.float32)
    fmin, fmax = 75.0, 500.0
    min_lag = int(sr / fmax)
    max_lag = int(sr / fmin)

    rms_global = np.sqrt(np.mean(x * x))
    noise_floor = max(1e-4, rms_global * 0.12)

    for i in range(0, len(x) - win_len, hop):
        seg = x[i:i + win_len]
        seg_rms = np.sqrt(np.mean(seg * seg))
        shift_semitones = 0.0

        if seg_rms > noise_floor:
            r = signal.correlate(seg, seg, mode="full")[win_len - 1:]
            if max_lag < len(r) and min_lag < max_lag:
                lag = np.argmax(r[min_lag:max_lag]) + min_lag
                peak_corr = r[lag] / (r[0] + 1e-9)
                if peak_corr > 0.40:
                    f0 = sr / lag
                    midi_val = 69.0 + 12.0 * np.log2(max(1.0, f0 / 440.0))
                    target_midi = snap_midi_to_scale(midi_val)
                    diff = target_midi - midi_val
                    if abs(diff) < 1.8:
                        shift_semitones = diff * strength

        if abs(shift_semitones) > 0.05:
            shifted = pitch_shift_vocoder(seg, shift_semitones, sr)
        else:
            shifted = seg

        out[i:i + win_len] += shifted * window
        norm[i:i + win_len] += window

    mask = norm > 1e-5
    out[mask] /= norm[mask]
    out[~mask] = x[~mask]
    return out.astype(np.float32)


def read_wav_float(path: str) -> np.ndarray:
    sr, data = wavfile.read(path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if data.dtype == np.int16:
        x = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        x = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.uint8:
        x = (data.astype(np.float32) - 128.0) / 128.0
    else:
        x = data.astype(np.float32)
    if sr != SR:
        # Remuestreo simple por interpolación lineal.
        n = int(round(len(x) * SR / sr))
        x = np.interp(
            np.linspace(0, len(x) - 1, n, dtype=np.float64),
            np.arange(len(x), dtype=np.float64),
            x,
        ).astype(np.float32)
    return x


def load_audio(path: str) -> np.ndarray:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".wav":
        return read_wav_float(path)

    # M4A, MP3, OGG...: decodificar con el ffmpeg que trae imageio.
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        subprocess.run(
            [ffmpeg, "-y", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
             "-sample_fmt", "s16", tmp_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return read_wav_float(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def save_audio(path: str, data: np.ndarray) -> None:
    peak = float(np.max(np.abs(data)))
    if peak > 0:
        data = data / peak * 0.95
    wavfile.write(path, SR, np.int16(np.clip(data, -1.0, 1.0) * 32767))


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x * x))) if len(x) else 0.0


def highpass(x: np.ndarray, cutoff: float = 85.0) -> np.ndarray:
    b, a = butter(2, cutoff / (SR / 2), btype="high")
    return lfilter(b, a, x).astype(np.float32)


def lowpass(x: np.ndarray, cutoff: float = 12500.0) -> np.ndarray:
    b, a = butter(2, cutoff / (SR / 2), btype="low")
    return lfilter(b, a, x).astype(np.float32)


def presence(x: np.ndarray, freq: float = 3000.0, gain_db: float = 2.0,
             q: float = 1.0) -> np.ndarray:
    # Filtro peaking RBJ.
    a_amp = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * freq / SR
    alpha = np.sin(w0) / (2.0 * q)
    b0 = 1.0 + alpha * a_amp
    b1 = -2.0 * np.cos(w0)
    b2 = 1.0 - alpha * a_amp
    a0 = 1.0 + alpha / a_amp
    a1 = -2.0 * np.cos(w0)
    a2 = 1.0 - alpha / a_amp
    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return lfilter(b, a, x).astype(np.float32)


def compress(x: np.ndarray, threshold_db: float = -18.0,
             ratio: float = 3.0, release: float = 0.06) -> np.ndarray:
    # Compresor suave con envolvente de un polo.
    alpha = float(np.exp(-1.0 / (SR * release)))
    env = lfilter([1.0 - alpha], [1.0, -alpha], np.abs(x))
    thresh = 10.0 ** (threshold_db / 20.0)
    gain = np.ones_like(env)
    mask = env > thresh
    gain[mask] = (thresh / env[mask]) ** (1.0 - 1.0 / ratio)
    return (x * gain).astype(np.float32)


def make_reverb_ir(dur: float = 0.9) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    b, a = butter(2, 5000.0 / (SR / 2), btype="low")
    ir = lfilter(b, a, noise) * np.exp(-t / 0.28)
    ir /= max(1e-9, float(np.sqrt(np.sum(ir * ir))))
    return ir


SECTION_TIMINGS = {
    "intro": 0.0,
    "verso1": 37.14,
    "verso-1": 37.14,
    "verso_1": 37.14,
    "coro1": 108.57,
    "coro-1": 108.57,
    "coro_1": 108.57,
    "primer_coro": 108.57,
    "primer-coro": 108.57,
    "primercoro": 108.57,
    "verso2": 148.57,
    "verso-2": 148.57,
    "verso_2": 148.57,
    "coro2": 240.0,
    "coro-2": 240.0,
    "coro_2": 240.0,
    "segundo_coro": 240.0,
    "segundo-coro": 240.0,
    "segundocoro": 240.0,
    "coro3": 280.0,
    "coro-3": 280.0,
    "coro_3": 280.0,
    "tercer_coro": 280.0,
    "tercer-coro": 280.0,
    "tercercoro": 280.0,
    "verso3": 317.14,
    "verso-3": 317.14,
    "verso_3": 317.14,
    "puente": 377.14,
    "bridge": 377.14,
    "outro": 397.14,
}


def guess_section_place(filename: str) -> tuple[str, float] | None:
    fn = filename.lower()
    for key, place in SECTION_TIMINGS.items():
        if key in fn:
            return key, place
    return None


def process_vocal_take(raw_vocal: np.ndarray, autotune_strength: float = 0.80) -> np.ndarray:
    v = highpass(raw_vocal)
    if autotune_strength > 0:
        v = autotune_vocal(v, strength=autotune_strength)
    v = lowpass(v)
    v = presence(v)
    v = compress(v)
    # Nivel base de la voz (aprox. -18 dBFS RMS).
    v = v / max(rms(v), 1e-6) * 0.12
    return v


def main() -> None:
    parser = argparse.ArgumentParser(description="Mezcla y afina voz + instrumental (por cachos o completa)")
    parser.add_argument("vocal", nargs="?", default=os.path.join(HERE, "voz"),
                        help="Archivo de audio o carpeta con los cachos (por defecto: music/voz/)")
    parser.add_argument("--instrumental", default=INSTRUMENTAL)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--trim", type=float, default=None,
                        help="Segundos a recortar del inicio (por defecto 1 compás si es toma completa)")
    parser.add_argument("--place", type=float, default=None,
                        help="Segundo de la canción donde entra la voz (por defecto detectado según el nombre)")
    parser.add_argument("--vocal-gain", type=float, default=1.0)
    parser.add_argument("--music-gain", type=float, default=0.85)
    parser.add_argument("--reverb", type=float, default=0.14)
    parser.add_argument("--autotune", type=float, default=0.80,
                        help="Fuerza de afinación a la escala (0.0 = apagado, 0.8 = natural, 1.0 = completo)")
    args = parser.parse_args()

    print("Cargando instrumental...")
    _, raw = wavfile.read(args.instrumental)
    inst = raw.astype(np.float32) / 32768.0
    inst = inst / max(rms(inst), 1e-6) * 0.10

    vocal_bus = np.zeros(len(inst), dtype=np.float32)
    files_to_process: list[tuple[str, float, float]] = [] # (path, place, trim)

    if os.path.isdir(args.vocal):
        exts = (".wav", ".m4a", ".mp3", ".webm", ".ogg")
        entries = sorted(os.listdir(args.vocal))
        audio_files = [os.path.join(args.vocal, f) for f in entries if f.lower().endswith(exts)]
        if not audio_files:
            print(f"No se encontraron archivos de audio en {args.vocal}.")
            print("Guarda allí tus cachos descargados del karaoke (ej: 01-intro.webm, 02-verso1.m4a, etc.).")
            return

        print(f"Se encontraron {len(audio_files)} toma(s) en {args.vocal}:")
        for f in audio_files:
            base = os.path.basename(f)
            guessed = guess_section_place(base)
            if guessed:
                sec_name, place = guessed
                trim = 0.0 # Los cachos por sección empiezan en su tiempo exacto
                files_to_process.append((f, place, trim))
                print(f"  • {base:25} -> Sección '{sec_name}' en {place:.2f}s")
            elif "voz-principal" in base.lower():
                trim = BAR if args.trim is None else args.trim
                place = 0.0 if args.place is None else args.place
                files_to_process.append((f, place, trim))
                print(f"  • {base:25} -> Canción completa (inicio {place:.2f}s, trim {trim:.2f}s)")
            else:
                place = 0.0 if args.place is None else args.place
                trim = 0.0 if args.trim is None else args.trim
                files_to_process.append((f, place, trim))
                print(f"  • {base:25} -> Posición {place:.2f}s")
    else:
        if not os.path.isfile(args.vocal):
            print(f"No existe el archivo o carpeta: {args.vocal}")
            return
        base = os.path.basename(args.vocal)
        guessed = guess_section_place(base)
        if args.place is not None:
            place = args.place
            trim = 0.0 if args.trim is None else args.trim
        elif guessed:
            _, place = guessed
            trim = 0.0 if args.trim is None else args.trim
        else:
            place = 0.0
            trim = BAR if args.trim is None else args.trim
        files_to_process.append((args.vocal, place, trim))

    # Procesar y ubicar cada cacho
    for fpath, place, trim in files_to_process:
        print(f"Procesando y afinando: {os.path.basename(fpath)}...")
        raw_v = load_audio(fpath)
        if trim > 0:
            raw_v = raw_v[int(trim * SR):]
        if len(raw_v) == 0:
            continue

        clean_v = process_vocal_take(raw_v, autotune_strength=args.autotune)
        start_samp = int(place * SR)
        end_samp = min(len(vocal_bus), start_samp + len(clean_v))
        if end_samp > start_samp:
            vocal_bus[start_samp:end_samp] += clean_v[: end_samp - start_samp]

    # Reverb amplio dream pop sobre el bus de voces
    if args.reverb > 0 and np.max(np.abs(vocal_bus)) > 1e-4:
        print("Aplicando reverberación Dream Pop a la voz...")
        wet = fftconvolve(vocal_bus, make_reverb_ir(), mode="full")[: len(vocal_bus)]
        vocal_bus = vocal_bus + wet.astype(np.float32) * args.reverb

    # Mezclar con la pista instrumental
    mix = np.zeros(len(inst), dtype=np.float32)
    mix += inst * args.music_gain
    mix += vocal_bus * args.vocal_gain

    # Suavizar picos y normalizar
    mix = np.tanh(mix * 0.92)
    save_audio(args.out, mix)
    print(f"\n✅ Canción mezclada y afinada lista:")
    print(f"   WAV: {args.out} ({len(mix) / SR:.1f} s)")

    # Exportar también en MP3 para escucharla en el celular fácilmente
    try:
        mp3_out = os.path.splitext(args.out)[0] + ".mp3"
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run(
            [ffmpeg, "-y", "-i", args.out, "-b:a", "192k", mp3_out],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"   MP3: {mp3_out}")
    except Exception as e:
        pass


if __name__ == "__main__":
    main()
