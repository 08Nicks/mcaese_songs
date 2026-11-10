# Guía para grabar la voz

## Antes de grabar

- Usa **audífonos**. Así el clic y la base no se cuelan en tu micrófono.
- Graba en un cuarto silencioso, con el celular o el micrófono cerca de la boca.
- Si puedes, graba en **WAV** o en la mayor calidad que te permita tu app. Si solo tienes M4A/MP3, también sirve.

## Pistas

| Pista | Para qué |
| --- | --- |
| `de-un-veremos-a-dos-anos-guia.wav` | 1 compás de conteo + instrumental. La canción empieza en **0:02.9**. |
| `de-un-veremos-a-dos-anos-click.wav` | Solo clic, por si grabas en un DAW y quieres el metrónomo aparte. |
| `de-un-veremos-a-dos-anos.wav` | Instrumental limpia, sin conteo. |

## Tiempos de la guía (con conteo)

| Sección | Empieza |
| --- | --- |
| Intro | 0:02.9 |
| Verso 1 | 0:40.0 |
| Primer Coro | 1:51.4 |
| Verso 2 | 2:31.4 |
| Segundo Coro | 4:02.9 |
| Tercer Coro | 4:42.9 |
| Verso 3 | 5:20.0 |
| Puente | 6:20.0 |
| Outro | 6:40.0 |
| Fin | 7:22.9 |

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
