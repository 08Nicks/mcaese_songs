"""
Genera music/karaoke-data.js y music/guia-de-grabacion.md a partir de
music/letra.txt y del plan de song_plan.py.

Cada línea lleva los tiempos de sus palabras, para que el karaoke ilumine
la palabra exacta que toca leer, al mismo paso de la base.
"""

from __future__ import annotations

import json
import os

from song_plan import (
    BAR,
    BPM,
    COUNT_IN,
    LINES,
    SECTIONS,
    SONG_SECONDS,
    TOTAL_BARS,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "karaoke-data.js")
GUIDE = os.path.join(HERE, "guia-de-grabacion.md")


def build_data() -> dict:
    sections = []
    for sec in SECTIONS:
        lines = []
        for line in sec["lines"]:
            lines.append({
                "text": line["text"],
                "start": line["start"],
                "end": line["end"],
                "words": line["words"],
            })
        sections.append({
            "name": sec["name"],
            "start": sec["start"],
            "end": sec["end"],
            "lines": lines,
        })

    return {
        "title": "De un «Veremos» a Dos Años",
        "bpm": BPM,
        "countIn": round(COUNT_IN, 3),
        "audio": "de-un-veremos-a-dos-anos.mp3",
        "guideAudio": "de-un-veremos-a-dos-anos-guia.mp3",
        "mixAudio": "de-un-veremos-a-dos-anos-mezcla.mp3",
        "duration": round(SONG_SECONDS, 3),
        "sections": sections,
    }


def fmt(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m}:{s:04.1f}"


def write_guide() -> None:
    rows = []
    for sec in SECTIONS:
        start = sec["start"] + COUNT_IN
        rows.append(f"| {sec['name']} | {fmt(start)} |")
    table = "\n".join(rows)

    text = f"""# Guía para grabar la voz

## Antes de grabar

- Usa **audífonos**. Así el clic y la base no se cuelan en tu micrófono.
- Graba en un cuarto silencioso, con el celular o el micrófono cerca de la boca.
- Si puedes, graba en **WAV** o en la mayor calidad que te permita tu app. Si solo tienes M4A/MP3, también sirve.

## Pistas

| Pista | Para qué |
| --- | --- |
| `de-un-veremos-a-dos-anos-guia.wav` | 1 compás de conteo + instrumental. La canción empieza en **{fmt(COUNT_IN)}**. |
| `de-un-veremos-a-dos-anos-click.wav` | Solo clic, por si grabas en un DAW y quieres el metrónomo aparte. |
| `de-un-veremos-a-dos-anos.wav` | Instrumental limpia, sin conteo. |

## Tiempos de la guía (con conteo)

| Sección | Empieza |
| --- | --- |
{table}
| Fin | {fmt(SONG_SECONDS + COUNT_IN)} |

## Grabar desde la página de karaoke

La página `music/player.html` ya trae la letra sincronizada palabra por palabra
y un botón para grabar:

1. Arranca el servidor desde la carpeta del proyecto:

   ```bash
   python serve.py
   ```

2. Abre http://127.0.0.1:4173/music/player.html
3. Ponte audífonos.
4. Pulsa **● Grabar mi voz**. Suena el conteo y empieza la canción.
5. Sigue la palabra iluminada y canta.
6. Al terminar, pulsa **■ Detener** y descarga `voz-principal.webm` (o `.m4a`).
7. Déjala en `music/voz/` y avísame.

## Cómo grabarla (con la pista guía)

1. Abre `player.html` o la pista `...-guia.wav`.
2. Escucha el conteo: **clic, clic, clic, clic**. Entras en la intro.
3. Puedes grabarla completa de una vez o por secciones. Si grabas por secciones, usa los tiempos de la tabla.
4. No importa si te sale una toma con respiraciones o ruido: yo la limpio y la mezclo.

## Dónde dejar la voz

- Crea o usa la carpeta `music/voz/`.
- Guarda tu archivo ahí, por ejemplo: `music/voz/voz-principal.wav`.
- Si grabaste en el celular, pásalo a la computadora con el mismo nombre.

Cuando esté ahí, avísame y yo la alineo con la instrumental, le quito ruido,
le pongo reverb y te entrego la mezcla.
"""
    with open(GUIDE, "w", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    data = build_data()
    body = json.dumps(data, ensure_ascii=False, indent=2)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("window.KARAOKE_DATA = ")
        f.write(body)
        f.write(";\n")

    write_guide()

    total_lines = sum(len(s["lines"]) for s in data["sections"])
    total_words = sum(len(l["words"]) for s in data["sections"] for l in s["lines"])
    print(f"{os.path.basename(OUT)}: {len(data['sections'])} secciones, "
          f"{total_lines} líneas, {total_words} palabras")
    print(f"{os.path.basename(GUIDE)} actualizada")
    print(f"{BPM} BPM · {TOTAL_BARS} compases · {SONG_SECONDS / 60:.2f} min · "
          f"conteo {COUNT_IN:.2f} s")
    for s in data["sections"]:
        print(f"  {s['name']:14} {s['start']:7.2f} - {s['end']:7.2f}  "
              f"({len(s['lines'])} líneas)")


if __name__ == "__main__":
    main()
