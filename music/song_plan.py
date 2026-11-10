"""
Plan musical y de tiempos de "De un «Veremos» a Dos Años".

Es la única fuente de verdad para:
  - make_song.py      (instrumental y MIDI)
  - make_karaoke.py   (letra y palabras sincronizadas)
  - make_guide.py     (pista guía y clic)
  - mix_vocal.py      (compás de conteo)

La letra se lee de letra.txt y se reparte por sílabas a un ritmo de flow
constante por sección. Así la palabra que se ilumina avanza al mismo paso
que la base, ni más rápido ni más lento.
"""

from __future__ import annotations

import math
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LYRICS_PATH = os.path.join(HERE, "letra.txt")

# ---------------------------------------------------------------------------
# Tempo y estructura
# ---------------------------------------------------------------------------

BPM = 84
BEAT = 60.0 / BPM
BAR = 4.0 * BEAT

# (encabezado en letra.txt, estilo musical)
SECTION_ORDER = [
    ("Intro", "intro"),
    ("Verso 1", "verse"),
    ("Primer Coro", "chorus"),
    ("Verso 2", "verse"),
    ("Segundo Coro", "chorus"),
    ("Tercer Coro", "chorus"),
    ("Verso 3", "verse3"),
    ("Puente", "bridge"),
    ("Outro", "outro"),
]

# Sílabas por tiempo (beat). Ajustado a 84 BPM (estilo MC Aese x Kali Uchis).
FLOW = {
    "intro": 3.0,
    "verse": 4.6,
    "verse3": 4.1,
    "chorus": 2.8,
    "bridge": 4.1,
    "outro": 2.8,
}

VOWELS = "aeiouü"


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def syllables(text: str) -> int:
    """Aproximación rápida: grupos de vocales."""
    base = strip_accents(text.lower())
    groups = re.findall(r"[aeiouü]+", base)
    return max(1, len(groups))


def hook_beats(text: str) -> float | None:
    t = text.lower().strip()
    if t.startswith("¡y tú") or t.startswith("¡túuu"):
        return 4.0
    if t.startswith("¡hey"):
        return 3.0 if "escucha" in t else 2.0
    return None


def parse_lyrics() -> dict[str, list[str]]:
    with open(LYRICS_PATH, encoding="utf-8") as f:
        raw = f.read()

    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("["):
            name = stripped[1:].split("]")[0]
            name = name.split(":")[0].strip()
            current = name
            sections.setdefault(current, [])
            continue
        if stripped.startswith("("):
            continue
        if current is None:
            continue
        sections[current].append(stripped)

    return sections


def build_plan() -> tuple[list[dict], list[dict], int]:
    parsed = parse_lyrics()
    sections: list[dict] = []
    all_lines: list[dict] = []
    cursor_bar = 0

    for header, style in SECTION_ORDER:
        raw_lines = parsed.get(header, [])
        if not raw_lines:
            raise SystemExit(f"No encontré líneas para la sección: {header}")

        durations: list[float] = []
        for text in raw_lines:
            fixed = hook_beats(text)
            if fixed is not None:
                beats = fixed
            else:
                beats = syllables(text) / FLOW[style]
                beats = max(1.0, round(beats * 4) / 4.0)
            durations.append(beats)

        used = sum(durations)
        bars = max(2, int(math.ceil(used / 4.0 - 1e-9)))

        section_start = cursor_bar * BAR
        line_cursor = 0.0
        lines: list[dict] = []

        for text, beats in zip(raw_lines, durations):
            start = section_start + line_cursor * BEAT
            end = start + beats * BEAT
            line = {
                "text": text,
                "start": round(start, 3),
                "end": round(end, 3),
                "syllables": syllables(text),
                "words": build_words(text, start, end),
            }
            lines.append(line)
            all_lines.append(line)
            line_cursor += beats

        sections.append({
            "name": header,
            "style": style,
            "start_bar": cursor_bar,
            "bars": bars,
            "start": round(section_start, 3),
            "end": round(section_start + bars * BAR, 3),
            "lines": lines,
        })
        cursor_bar += bars

    return sections, all_lines, cursor_bar


def build_words(text: str, start: float, end: float) -> list[dict]:
    tokens = text.split()
    if not tokens:
        return []

    weights = [max(1, syllables(tok)) for tok in tokens]
    total = float(sum(weights))
    duration = end - start
    words: list[dict] = []
    cursor = start

    for i, (tok, weight) in enumerate(zip(tokens, weights)):
        if i == len(tokens) - 1:
            word_end = end
        else:
            word_end = cursor + duration * weight / total
        words.append({
            "text": tok,
            "start": round(cursor, 3),
            "end": round(word_end, 3),
        })
        cursor = word_end

    return words


SECTIONS, LINES, TOTAL_BARS = build_plan()
SONG_SECONDS = TOTAL_BARS * BAR
TAIL_SECONDS = 3.0

# Tiempos de referencia (con conteo = 1 compás).
COUNT_IN = BAR


def section_times() -> list[dict]:
    out = []
    for s in SECTIONS:
        out.append({
            "name": s["name"],
            "bars": s["bars"],
            "start": s["start"],
            "end": s["end"],
            "guide_start": s["start"] + COUNT_IN,
            "guide_end": s["end"] + COUNT_IN,
        })
    return out


if __name__ == "__main__":
    print(f"{BPM} BPM · compás {BAR:.3f} s · {TOTAL_BARS} compases · "
          f"{SONG_SECONDS / 60:.2f} min")
    for s in SECTIONS:
        print(f"  {s['name']:14} {s['bars']:3} compases  "
              f"{s['start']:7.2f} - {s['end']:7.2f} s  "
              f"({len(s['lines'])} líneas)")
    print(f"Total líneas: {len(LINES)}")
