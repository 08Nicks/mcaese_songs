# De un «Veremos» a Dos Años — instrumental

Maqueta instrumental de la canción en estilo **fusión romántica**:
- **MC Aese («Beso a Beso»)**: guitarra acústica arpegiada íntima y versos cálidos.
- **Kali Uchis («Telepatía»)**: piano eléctrico Rhodes con chorus, pads celestiales, bajo suave y groove de dembow lento/R&B sensual.
- **Tempo:** 84 BPM, 4/4, La menor / Do mayor.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `de-un-veremos-a-dos-anos.wav` | Maqueta instrumental completa (6:03) |
| `de-un-veremos-a-dos-anos-guia.wav` | 1 compás de conteo + instrumental, para grabar la voz |
| `de-un-veremos-a-dos-anos-click.wav` | Solo clic, para grabar en un DAW |
| `de-un-veremos-a-dos-anos.mid` | MIDI editable (piano, guitarra, cuerdas, coro, bronces, 808, batería) |
| `letra.txt` | Letra completa original |
| `prompt-ia.txt` | Estilo + letra condensada para Suno/Udio |
| `karaoke-data.js` | Tiempos de la letra para el karaoke (generado) |
| `guia-de-grabacion.md` | Tiempos, consejos y dónde dejar la voz |
| `voz/` | Carpeta para tu grabación |
| `make_song.py` | Script que genera el WAV y el MIDI |
| `make_guide.py` | Script que genera la guía y el clic |
| `make_karaoke.py` | Script que genera `karaoke-data.js` desde `letra.txt` |
| `mix_vocal.py` | Script que mezcla tu voz con la instrumental |
| `player.html` | Karaoke: letra sincronizada + grabación de voz |
| `../serve.py` | Servidor local con soporte de audio (Range) |

## Escuchar y cantar

Sirve la carpeta con el servidor incluido (no uses `python -m http.server`:
no soporta *Range* y el audio se traba al buscar dentro de la canción):

```bash
python serve.py
```

Luego abre:

- **App:** http://127.0.0.1:4173/index.html
- **Karaoke:** http://127.0.0.1:4173/music/player.html

En el karaoke puedes cambiar entre la pista con conteo y la instrumental limpia,
ver la **palabra exacta** iluminarse al ritmo de la base y grabar tu voz con el
micrófono.

## Grabar desde el karaoke

1. Usa **audífonos** (así el micrófono no captura la pista).
2. Pulsa **● Grabar mi voz**: suena el conteo de 4 tiempos y empieza la canción.
3. Canta siguiendo la palabra que se ilumina.
4. Pulsa **■ Detener** y descarga el archivo (`voz-principal.webm` o `.m4a`).
5. Déjalo en `music/voz/` y avísame para mezclarlo.

Si el navegador no da acceso al micrófono, revisa los permisos del sitio o graba
con la app del celular sobre `de-un-veremos-a-dos-anos-guia.wav`.

## Estructura

| Sección | Compases | Tiempo | Acompañamiento |
| --- | --- | --- | --- |
| Intro | 1–12 | 0:00–0:30 | Piano oscuro, cuerdas graves y ambiente; graves y medios, sin brillo |
| Verso 1 | 13–35 | 0:30–1:27.5 | 808, batería con groove, guitarra nylon y piano |
| Coro 1 | 36–48 | 1:27.5–2:00 | Pesado y emotivo: cuerdas agudas, coro, bronces, crash |
| Verso 2 | 49–78 | 2:00–3:15 | Groove completo, oscuro y medio |
| Coro 2 | 79–91 | 3:15–3:47.5 | Completo, más intenso |
| Coro 3 | 92–103 | 3:47.5–4:17.5 | Completo, el punto más alto y pesado |
| Verso 3 | 104–123 | 4:17.5–5:07.5 | Doloroso: piano agudo, cuerdas agudas con trémolo, medios al frente |
| Puente | 124–130 | 5:07.5–5:25 | Batería four-on-the-floor, bronces y riser |
| Outro | 131–144 | 5:25–6:00 | Regresa lo oscuro: piano y cuerdas graves, fade out |

## Para una producción real

1. Importa el `.mid` en Reaper, FL Studio, Ableton o GarageBand.
2. Pon el tempo en **96 BPM** y el compás en **4/4**.
3. Cambia el piano por uno oscuro/cinematográfico (LABS Soft Piano, Keyscape, Addictive Keys).
4. Cuerdas: usa un banco de cuerdas reales (Spitfire, Kontakt, LABS Strings) y sube las agudas en coros y Verso 3.
5. Coro y bronces: pads vocales y metales para dar drama; no los pongas al frente, son soporte.
6. Batería: trap/dembow; bombo en 1 y 2.5, caja en 2 y 4, hi-hats en 8vos y 16vos.
7. 808: notas raíz con deslizamientos y sidechain suave con el bombo.
8. Mezcla: 808 y bombo con peso pero sin tapar los medios; cuerdas agudas y voz al frente; reverb de sala grande.

## Voz

- **Grabarla tú:** usa `de-un-veremos-a-dos-anos-guia.wav` (tiene 1 compás de conteo) o el MIDI en tu DAW. La letra completa está en `letra.txt`.
- **Con IA:** pega el estilo y la letra de `prompt-ia.txt` en Suno o Udio. Si el plan limita caracteres, genera la primera parte y usa **Extend** para el resto.

## Mezclar tu voz y afinarla

1. Graba con la pista guía (o desde la web de karaoke) y guarda el archivo en `music/voz/voz-principal.wav` (o `.webm`, `.m4a`, `.mp3`).
2. Ejecuta:

   ```bash
   python music/mix_vocal.py music/voz/voz-principal.wav
   ```

   El script incluye **afinador automático (Pitch Correction)** a la escala de La menor / Do mayor, ecualización de presencia y aire, compresión suave, reverb dream pop y balance final.

3. La mezcla lista sale en `music/de-un-veremos-a-dos-anos-mezcla.wav`.

Si grabaste sobre la instrumental limpia (sin el conteo), usa `--trim 0`.
Si grabaste solo una sección, usa `--trim 0 --place SEGUNDOS` (por ejemplo, `--place 87.5` para el Coro 1).

## Nota

El WAV no trae voz: es la base instrumental. La canción "de verdad" se completa
grabando la voz encima o generándola con una IA de música.
