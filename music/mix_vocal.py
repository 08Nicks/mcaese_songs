"""
Mezcla y afinación (Auto-Tune) de la voz con la instrumental de "De un «Veremos» a Dos Años".

Estilo de producción:
- Kali Uchis «Telepatía»: voces aéreas, dream pop reverb estéreo, delay sincronizado con ducking,
  y afinación sutil a la escala (La menor / Do mayor).
- MC Aese «Beso a Beso»: intimidad acústica, presencia cercana, dinámica balanceada y claridad en cada palabra.

Uso:
    python music/mix_vocal.py
    python music/mix_vocal.py music/voz/
    python music/mix_vocal.py music/voz/ --autotune 0.85
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import imageio_ffmpeg
import numpy as np
from scipy import signal
from scipy.io import wavfile

from song_plan import BAR, BEAT, BPM

SR = 32000
HERE = os.path.dirname(os.path.abspath(__file__))
INSTRUMENTAL = os.path.join(HERE, "de-un-veremos-a-dos-anos.wav")
DEFAULT_OUT = os.path.join(HERE, "de-un-veremos-a-dos-anos-mezcla.wav")

# Escala de La menor / Do mayor: C (0), D (2), E (4), F (5), G (7), A (9), B (11)
SCALE_NOTES = [0, 2, 4, 5, 7, 9, 11]

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
    "verso2": 148.57,
    "verso-2": 148.57,
    "verso_2": 148.57,
    "coro2": 240.0,
    "coro-2": 240.0,
    "coro_2": 240.0,
    "segundo_coro": 240.0,
    "coro3": 280.0,
    "coro-3": 280.0,
    "coro_3": 280.0,
    "tercer_coro": 280.0,
    "verso3": 317.14,
    "verso-3": 317.14,
    "verso_3": 317.14,
    "puente": 377.14,
    "bridge": 377.14,
    "outro": 397.14,
}

NUM_MAP = {
    "01": ("intro", 0.0),
    "02": ("verso1", 37.14),
    "03": ("coro1", 108.57),
    "04": ("verso2", 148.57),
    "05": ("coro2", 240.0),
    "06": ("coro3", 280.0),
    "07": ("verso3", 317.14),
    "08": ("puente", 377.14),
    "09": ("outro", 397.14),
}


def snap_midi_to_scale(midi_val: float) -> float:
    semitone = int(round(midi_val))
    pc = semitone % 12
    best_pc = min(SCALE_NOTES, key=lambda note: min(abs(pc - note), 12 - abs(pc - note)))
    diff = (best_pc - pc + 6) % 12 - 6
    return float(semitone + diff)


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
    """Guarda en WAV estéreo o mono normalizado a -0.3 dBFS."""
    peak = float(np.max(np.abs(data)))
    if peak > 0:
        target_peak = 10.0 ** (-0.3 / 20.0) # ~0.966
        data = data / peak * target_peak
    audio = np.int16(np.clip(data, -1.0, 1.0) * 32767)
    wavfile.write(path, SR, audio)


# ---------------------------------------------------------------------------
# Procesamiento de Señal Vocal (Filtros, Dinámica, Ecualización)
# ---------------------------------------------------------------------------

def highpass(x: np.ndarray, cutoff: float = 85.0) -> np.ndarray:
    """Corte de subgraves y ruido de manejo del micrófono."""
    b, a = signal.butter(2, cutoff / (SR / 2), btype="high")
    return signal.lfilter(b, a, x).astype(np.float32)


def lowpass(x: np.ndarray, cutoff: float = 14500.0) -> np.ndarray:
    """Suavizado de frecuencias ultrasónicas."""
    b, a = signal.butter(2, cutoff / (SR / 2), btype="low")
    return signal.lfilter(b, a, x).astype(np.float32)


def biquad_peak(x: np.ndarray, freq: float, gain_db: float, q: float = 1.0) -> np.ndarray:
    """Filtro de campana paramétrico RBJ."""
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * freq / SR
    alpha = np.sin(w0) / (2.0 * q)
    b0 = 1.0 + alpha * A
    b1 = -2.0 * np.cos(w0)
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * np.cos(w0)
    a2 = 1.0 - alpha / A
    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return signal.lfilter(b, a, x).astype(np.float32)


def biquad_high_shelf(x: np.ndarray, freq: float, gain_db: float) -> np.ndarray:
    """High shelf RBJ para brillo sedoso de gama alta."""
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * freq / SR
    cosw0 = np.cos(w0)
    sinw0 = np.sin(w0)
    alpha = sinw0 / 2.0 * np.sqrt(2.0)
    b0 = A * ((A + 1.0) + (A - 1.0) * cosw0 + 2.0 * np.sqrt(A) * alpha)
    b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cosw0)
    b2 = A * ((A + 1.0) + (A - 1.0) * cosw0 - 2.0 * np.sqrt(A) * alpha)
    a0 = (A + 1.0) - (A - 1.0) * cosw0 + 2.0 * np.sqrt(A) * alpha
    a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cosw0)
    a2 = (A + 1.0) - (A - 1.0) * cosw0 - 2.0 * np.sqrt(A) * alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return signal.lfilter(b, a, x).astype(np.float32)


def deess(x: np.ndarray, freq: float = 6800.0, thresh_db: float = -20.0) -> np.ndarray:
    """De-esser para suavizar sibilancias agudas molestas."""
    b, a = signal.butter(2, freq / (SR / 2), btype="high")
    highs = signal.lfilter(b, a, x)
    alpha = np.exp(-1.0 / (SR * 0.02))
    env = signal.lfilter([1.0 - alpha], [1.0, -alpha], np.abs(highs))
    thresh = 10.0 ** (thresh_db / 20.0)
    atten = np.ones_like(env)
    mask = env > thresh
    atten[mask] = (thresh / env[mask]) ** 0.5
    return (x * atten).astype(np.float32)


def noise_gate(x: np.ndarray, thresh_db: float = -38.0, reduction_db: float = 24.0) -> np.ndarray:
    """Expansor descendente suave para limpiar pausas entre frases."""
    alpha_att = float(np.exp(-1.0 / (SR * 0.012)))
    alpha_rel = float(np.exp(-1.0 / (SR * 0.080)))
    thresh = 10.0 ** (thresh_db / 20.0)
    min_gain = 10.0 ** (-reduction_db / 20.0)

    abs_x = np.abs(x)
    env = np.zeros_like(x)
    curr = 0.0
    for i in range(len(x)):
        val = abs_x[i]
        curr = alpha_att * curr + (1.0 - alpha_att) * val if val > curr else alpha_rel * curr + (1.0 - alpha_rel) * val
        env[i] = curr

    gain = np.ones_like(x)
    mask = env < thresh
    ratio = np.clip(env[mask] / thresh, 0.0, 1.0)
    gain[mask] = min_gain + (1.0 - min_gain) * (0.5 - 0.5 * np.cos(np.pi * ratio))
    return (x * gain).astype(np.float32)


def compress(x: np.ndarray, threshold_db: float = -18.0, ratio: float = 3.2, release: float = 0.07) -> np.ndarray:
    """Compresión óptica suave que aporta cuerpo y uniformidad."""
    alpha = float(np.exp(-1.0 / (SR * release)))
    env = signal.lfilter([1.0 - alpha], [1.0, -alpha], np.abs(x))
    thresh = 10.0 ** (threshold_db / 20.0)
    gain = np.ones_like(env)
    mask = env > thresh
    gain[mask] = (thresh / env[mask]) ** (1.0 - 1.0 / ratio)
    return (x * gain).astype(np.float32)


def active_speech_rms(x: np.ndarray) -> float:
    """Calcula el RMS solo de los fragmentos donde hay voz activa."""
    win = int(0.04 * SR)
    if len(x) < win:
        return float(np.sqrt(np.mean(x * x))) if len(x) else 1e-4
    energies = [np.sqrt(np.mean(x[i:i + win] ** 2)) for i in range(0, len(x) - win, win)]
    arr = np.array(energies)
    pos = arr[arr > 0.008]
    if len(pos) == 0:
        return max(1e-4, float(np.sqrt(np.mean(x * x))))
    p30 = np.percentile(pos, 30)
    top_frames = pos[pos >= p30]
    return float(np.mean(top_frames)) if len(top_frames) else 1e-4


# ---------------------------------------------------------------------------
# Afinación Inteligente (Auto-Tune PSOLA a la Escala)
# ---------------------------------------------------------------------------

def autotune_vocal_psola(x: np.ndarray, strength: float = 0.82, retune_ms: float = 28.0) -> np.ndarray:
    """
    Afinación de alta fidelidad con preservación de formantes y consonantes.
    Detecta la frecuencia fundamental y la ajusta suavemente hacia las notas
    de la escala musical (La menor / Do mayor).
    """
    if len(x) == 0 or strength <= 0.0:
        return x

    hop = int(0.015 * SR)      # Análisis cada 15 ms
    win_len = int(0.045 * SR)  # Ventana de 45 ms
    fmin, fmax = 75.0, 480.0
    min_lag = int(SR / fmax)
    max_lag = int(SR / fmin)

    n_frames = (len(x) - win_len) // hop
    raw_shifts = np.zeros(n_frames, dtype=np.float32)
    voiced = np.zeros(n_frames, dtype=bool)
    f0_track = np.zeros(n_frames, dtype=np.float32)

    # Umbral de ruido adaptativo
    rms_arr = np.array([np.sqrt(np.mean(x[i * hop:i * hop + win_len] ** 2)) for i in range(n_frames)])
    active_rms = rms_arr[rms_arr > 0.01]
    noise_floor = np.percentile(active_rms, 10) * 0.3 if len(active_rms) > 0 else 0.004

    for k in range(n_frames):
        if rms_arr[k] < noise_floor:
            continue
        seg = x[k * hop:k * hop + win_len]
        r = signal.correlate(seg, seg, mode="full")[win_len - 1:]
        if max_lag < len(r):
            lag = np.argmax(r[min_lag:max_lag]) + min_lag
            peak_corr = r[lag] / (r[0] + 1e-9)
            if peak_corr > 0.40:
                f0 = SR / lag
                f0_track[k] = f0
                midi_val = 69.0 + 12.0 * np.log2(f0 / 440.0)
                target = snap_midi_to_scale(midi_val)
                diff = target - midi_val
                # Solo corregimos dentro del rango de tolerancia musical (+-1.6 semitonos)
                if abs(diff) <= 1.6:
                    raw_shifts[k] = diff * strength
                    voiced[k] = True

    # Suavizado temporal de afinación (retune speed)
    tau_samples = int((retune_ms / 1000.0) / (hop / SR))
    smoothed_shifts = raw_shifts.copy()
    if tau_samples > 1:
        alpha = np.exp(-1.0 / tau_samples)
        s = 0.0
        for i in range(n_frames):
            if voiced[i]:
                s = alpha * s + (1.0 - alpha) * raw_shifts[i]
                smoothed_shifts[i] = s
            else:
                s = 0.0
                smoothed_shifts[i] = 0.0

    # Resíntesis PSOLA por granos solapados
    grain_len = int(0.040 * SR)
    grain_hop = int(0.010 * SR)
    hanning_grain = np.hanning(grain_len).astype(np.float32)

    out = np.zeros_like(x)
    norm = np.zeros_like(x)

    for i in range(0, len(x) - grain_len, grain_hop):
        frame_idx = min(n_frames - 1, i // hop)
        shift = smoothed_shifts[frame_idx]
        grain = x[i:i + grain_len]

        if abs(shift) > 0.05 and voiced[frame_idx] and f0_track[frame_idx] > 0:
            factor = 2.0 ** (shift / 12.0)
            T0 = int(round(SR / f0_track[frame_idx]))
            T1 = int(round(T0 / factor))
            if min_lag <= T1 <= max_lag and 2 * T0 < grain_len:
                g_out = np.zeros(grain_len, dtype=np.float32)
                g_norm = np.zeros(grain_len, dtype=np.float32)
                t_out = T0
                w_size = 2 * T0
                w_half = w_size // 2
                h_win = np.hanning(w_size).astype(np.float32)
                while t_out < grain_len - w_half:
                    center = int(round(t_out / factor))
                    if w_half <= center < grain_len - w_half:
                        g_start = t_out - w_half
                        g_end = t_out + w_half
                        if 0 <= g_start and g_end <= grain_len:
                            g_out[g_start:g_end] += grain[center - w_half:center + w_half] * h_win
                            g_norm[g_start:g_end] += h_win
                    t_out += T1
                m = g_norm > 1e-4
                shifted_grain = grain.copy()
                shifted_grain[m] = g_out[m] / g_norm[m]
            else:
                shifted_grain = grain
        else:
            shifted_grain = grain

        out[i:i + grain_len] += shifted_grain * hanning_grain
        norm[i:i + grain_len] += hanning_grain

    mask = norm > 1e-4
    out[mask] /= norm[mask]
    out[~mask] = x[~mask]
    return out.astype(np.float32)


def process_vocal_take(raw: np.ndarray, autotune_strength: float = 0.82) -> np.ndarray:
    """Cadena completa de tratamiento vocal para cada cacho."""
    # 1. Filtro paso alto para limpiar rumble
    v = highpass(raw, cutoff=85.0)

    # 2. Afinación inteligente a la escala musical
    if autotune_strength > 0:
        v = autotune_vocal_psola(v, strength=autotune_strength, retune_ms=28.0)

    # 3. Ecualización quirúrgica de voz (calidez y presencia)
    # Limpiar resonancia de celular en 420 Hz (-1.8 dB)
    v = biquad_peak(v, freq=420.0, gain_db=-1.8, q=1.2)
    # Realzar presencia y dicción en 3.2 kHz (+2.2 dB)
    v = biquad_peak(v, freq=3200.0, gain_db=2.2, q=1.0)
    # Brillo sedoso arriba de 10.5 kHz (+2.4 dB)
    v = biquad_high_shelf(v, freq=10500.0, gain_db=2.4)
    # De-esser en 6.8 kHz
    v = deess(v, freq=6800.0, thresh_db=-22.0)
    v = lowpass(v, cutoff=14500.0)

    # 4. Puerta de ruido y compresión óptica
    v = noise_gate(v, thresh_db=-38.0, reduction_db=24.0)
    v = compress(v, threshold_db=-18.0, ratio=3.2)

    # 5. Normalización según nivel de voz activa (RMS constante ~0.115)
    sp_rms = active_speech_rms(v)
    v = v / max(sp_rms, 1e-4) * 0.115

    # 6. Fundidos suaves al borde para evitar chasquidos
    fade_in = int(0.04 * SR)
    fade_out = int(0.08 * SR)
    if len(v) > fade_in + fade_out:
        v[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
        v[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)

    return v


# ---------------------------------------------------------------------------
# Espacialización Estéreo Dream Pop (Reverb + Delay Ducked + Doubler)
# ---------------------------------------------------------------------------

def make_stereo_reverb_ir(decay_s: float = 1.7, pre_delay_ms: float = 24.0) -> tuple[np.ndarray, np.ndarray]:
    """Crea una respuesta al impulso estéreo decorrelada estilo placa/hall."""
    n = int(decay_s * SR)
    t = np.arange(n) / SR
    pre_samp = int(pre_delay_ms / 1000.0 * SR)

    np.random.seed(1337)
    noise_l = np.random.randn(n)
    noise_r = np.random.randn(n)

    b_h, a_h = signal.butter(2, 320.0 / (SR / 2), btype="high")
    b_l, a_l = signal.butter(2, 5400.0 / (SR / 2), btype="low")

    env = np.exp(-3.2 * t / decay_s)
    ir_l = signal.lfilter(b_l, a_l, signal.lfilter(b_h, a_h, noise_l)) * env
    ir_r = signal.lfilter(b_l, a_l, signal.lfilter(b_h, a_h, noise_r)) * env

    # Pre-delay
    if pre_samp > 0:
        ir_l = np.pad(ir_l, (pre_samp, 0))[:n]
        ir_r = np.pad(ir_r, (pre_samp, 0))[:n]

    ir_l /= max(1e-6, float(np.sqrt(np.sum(ir_l * ir_l))))
    ir_r /= max(1e-6, float(np.sqrt(np.sum(ir_r * ir_r))))
    return ir_l.astype(np.float32), ir_r.astype(np.float32)


def apply_ducked_stereo_delay(vocal: np.ndarray, bpm: float = 84.0, wet: float = 0.11) -> tuple[np.ndarray, np.ndarray]:
    """Echo estéreo sincronizado que se atenúa mientras se canta y resuena en pausas."""
    beat = 60.0 / bpm
    d_l = int(0.5 * beat * SR)  # Corchea izquierda (~357 ms)
    d_r = int(0.75 * beat * SR) # Corchea con punto derecha (~536 ms)

    # Envolvente para ducking
    alpha = np.exp(-1.0 / (SR * 0.05))
    env = signal.lfilter([1.0 - alpha], [1.0, -alpha], np.abs(vocal))
    duck_gain = 1.0 / (1.0 + 7.0 * (env / 0.08))

    send = vocal * duck_gain
    n = len(vocal)

    out_l = np.zeros(n, dtype=np.float32)
    out_r = np.zeros(n, dtype=np.float32)

    # 3 repeticiones por canal
    for tap, gain in enumerate([1.0, 0.30, 0.09], start=1):
        dl_k = tap * d_l
        dr_k = tap * d_r
        if dl_k < n:
            out_l[dl_k:] += send[:-dl_k] * gain
        if dr_k < n:
            out_r[dr_k:] += send[:-dr_k] * gain

    # Filtro cálido analógico
    b_lp, a_lp = signal.butter(1, 3800.0 / (SR / 2), btype="low")
    out_l = signal.lfilter(b_lp, a_lp, out_l) * wet
    out_r = signal.lfilter(b_lp, a_lp, out_r) * wet
    return out_l.astype(np.float32), out_r.astype(np.float32)


def guess_section_place(filename: str) -> tuple[str, float] | None:
    fn = filename.lower()
    for prefix, val in NUM_MAP.items():
        if fn.startswith(prefix) or f"-{prefix}-" in fn or f"_{prefix}_" in fn:
            return val
    for key, place in SECTION_TIMINGS.items():
        if key in fn:
            return key, place
    return None


# ---------------------------------------------------------------------------
# Pipeline Principal de Mezcla
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Mezcla profesional y afinación de voz + instrumental")
    parser.add_argument("vocal", nargs="?", default=os.path.join(HERE, "voz"),
                        help="Carpeta con los cachos o archivo individual (por defecto: music/voz/)")
    parser.add_argument("--instrumental", default=INSTRUMENTAL)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--vocal-gain", type=float, default=1.0)
    parser.add_argument("--music-gain", type=float, default=0.88)
    parser.add_argument("--reverb", type=float, default=0.15)
    parser.add_argument("--delay", type=float, default=0.10)
    parser.add_argument("--autotune", type=float, default=0.82,
                        help="Fuerza de afinación a la escala (0.0 = apagado, 0.8 = natural/estudio, 1.0 = completo)")
    args = parser.parse_args()

    t_start = time.time()
    print("=================================================================")
    print("🎵 DE UN «VEREMOS» A DOS AÑOS — MEZCLA FINAL Y MASTERIZACIÓN")
    print("   Estilo: Fusión Romántica MC Aese x Kali Uchis (84 BPM)")
    print("=================================================================\n")

    print("1. Cargando pista instrumental...")
    _, raw_inst = wavfile.read(args.instrumental)
    inst_mono = raw_inst.astype(np.float32) / 32768.0
    inst_mono = inst_mono / max(float(np.sqrt(np.mean(inst_mono * inst_mono))), 1e-4) * 0.125
    total_len = len(inst_mono)

    # Identificar archivos de voz
    files_to_process: list[tuple[str, float, float]] = [] # (path, place, trim)

    if os.path.isdir(args.vocal):
        exts = (".wav", ".m4a", ".mp3", ".webm", ".ogg")
        entries = sorted(os.listdir(args.vocal))
        audio_files = [os.path.join(args.vocal, f) for f in entries if f.lower().endswith(exts)]
        if not audio_files:
            print(f"❌ No se encontraron archivos de audio en {args.vocal}.")
            return

        print(f"2. Se encontraron {len(audio_files)} cacho(s) grabados:")
        for f in audio_files:
            base = os.path.basename(f)
            guessed = guess_section_place(base)
            if guessed:
                sec_name, place = guessed
                trim = 0.0
                files_to_process.append((f, place, trim))
                print(f"   • {base:24} -> Sección '{sec_name:10}' en {place:6.2f} s")
            elif "voz-principal" in base.lower():
                trim = BAR
                place = 0.0
                files_to_process.append((f, place, trim))
                print(f"   • {base:24} -> Toma completa (inicio {place:.2f} s)")
            else:
                place = 0.0
                trim = 0.0
                files_to_process.append((f, place, trim))
                print(f"   • {base:24} -> Posición manual {place:.2f} s")
    else:
        if not os.path.isfile(args.vocal):
            print(f"❌ No existe: {args.vocal}")
            return
        base = os.path.basename(args.vocal)
        guessed = guess_section_place(base)
        place = guessed[1] if guessed else 0.0
        files_to_process.append((args.vocal, place, 0.0))

    # Bus maestro de voces
    vocal_bus = np.zeros(total_len, dtype=np.float32)

    print("\n3. Procesando, ecualizando y afinando cada cacho con Auto-Tune...")
    for fpath, place, trim in files_to_process:
        base = os.path.basename(fpath)
        raw_v = load_audio(fpath)
        if trim > 0:
            raw_v = raw_v[int(trim * SR):]
        if len(raw_v) == 0:
            continue

        clean_v = process_vocal_take(raw_v, autotune_strength=args.autotune)
        start_samp = int(place * SR)
        end_samp = min(total_len, start_samp + len(clean_v))
        if end_samp > start_samp:
            vocal_bus[start_samp:end_samp] += clean_v[: end_samp - start_samp]
            print(f"   ✓ Afinado y posicionado: {base:22} ({len(clean_v)/SR:5.1f}s a {place:6.2f}s)")

    print("\n4. Generando espacialización estéreo Dream Pop (Reverb + Delay + Doubler)...")
    # A. Lead vocal central
    lead_dry = vocal_bus * args.vocal_gain

    # B. Micro-pitch Doubler estéreo (anchura de voz Kali Uchis)
    doubler_l_samp = int(0.013 * SR)
    doubler_r_samp = int(0.019 * SR)
    doubler_l = np.zeros(total_len, dtype=np.float32)
    doubler_r = np.zeros(total_len, dtype=np.float32)
    doubler_l[doubler_l_samp:] = vocal_bus[:-doubler_l_samp] * 0.14
    doubler_r[doubler_r_samp:] = vocal_bus[:-doubler_r_samp] * 0.14

    # C. Reverb estéreo amplio
    if args.reverb > 0:
        ir_l, ir_r = make_stereo_reverb_ir(decay_s=1.7, pre_delay_ms=25.0)
        rev_l = signal.fftconvolve(vocal_bus, ir_l, mode="full")[:total_len] * args.reverb
        rev_r = signal.fftconvolve(vocal_bus, ir_r, mode="full")[:total_len] * args.reverb
    else:
        rev_l = np.zeros(total_len, dtype=np.float32)
        rev_r = np.zeros(total_len, dtype=np.float32)

    # D. Delay estéreo con ducking
    if args.delay > 0:
        del_l, del_r = apply_ducked_stereo_delay(vocal_bus, bpm=BPM, wet=args.delay)
    else:
        del_l = np.zeros(total_len, dtype=np.float32)
        del_r = np.zeros(total_len, dtype=np.float32)

    # Bus estéreo vocal completo
    vocal_stereo_l = lead_dry + doubler_l + rev_l + del_l
    vocal_stereo_r = lead_dry + doubler_r + rev_r + del_r

    print("\n5. Aplicando sidechain ducking y mezclando con la instrumental...")
    # Sidechain: atenuar sutilmente la instrumental (~1.2 dB) cuando la voz canta
    alpha_duck = float(np.exp(-1.0 / (SR * 0.05)))
    vocal_env = signal.lfilter([1.0 - alpha_duck], [1.0, -alpha_duck], np.abs(vocal_bus))
    inst_duck = 1.0 / (1.0 + 1.8 * (vocal_env / 0.11))

    inst_ducked = inst_mono * inst_duck * args.music_gain

    # Instrumental estéreo con sutil apertura en medios/agudos
    b_mid, a_mid = signal.butter(2, [350.0 / (SR / 2), 7000.0 / (SR / 2)], btype="band")
    inst_mid = signal.lfilter(b_mid, a_mid, inst_ducked)
    inst_side_samp = int(0.007 * SR) # 7 ms Haas spread sutil
    inst_l = inst_ducked.copy()
    inst_r = inst_ducked.copy()
    inst_r[inst_side_samp:] += inst_mid[:-inst_side_samp] * 0.18
    inst_l[inst_side_samp:] -= inst_mid[:-inst_side_samp] * 0.18

    # Mezcla estéreo final
    mix_l = inst_l + vocal_stereo_l
    mix_r = inst_r + vocal_stereo_r

    print("\n6. Masterización analógica suave y limitación de picos...")
    # Saturación analógica tipo cinta (tape saturation suave)
    mix_l = np.tanh(mix_l * 0.94)
    mix_r = np.tanh(mix_r * 0.94)

    # Fundido final de salida suave en los últimos 4 segundos
    fade_len = int(4.0 * SR)
    fade_curve = np.linspace(1.0, 0.0, fade_len)
    mix_l[-fade_len:] *= fade_curve
    mix_r[-fade_len:] *= fade_curve

    stereo_out = np.column_stack([mix_l, mix_r])
    save_audio(args.out, stereo_out)

    mp3_out = os.path.splitext(args.out)[0] + ".mp3"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-i", args.out, "-b:a", "192k", mp3_out],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    elapsed = time.time() - t_start
    print("\n=================================================================")
    print(f"✨ ¡CANCIÓN COMPLETA MEZCLADA Y MASTERIZADA CON ÉXITO! ({elapsed:.1f}s)")
    print(f"   📁 WAV: {args.out} ({len(stereo_out) / SR:.1f} s, estéreo)")
    print(f"   📁 MP3: {mp3_out} ({os.path.getsize(mp3_out) / 1e6:.2f} MB)")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
