# MC AESE · Setlist Puebla & CDMX

Web estática para seguir el setlist del concierto, guardar tus letras y usarlas en modo concierto desde el celular.

No necesita instalación, servidor ni cuenta: son cuatro archivos.

## Cómo abrirla

**Opción rápida:** abre `index.html` con doble clic.

**Opción recomendada para el celular:** publica la carpeta en un hosting estático (Netlify Drop, GitHub Pages, Vercel) y abre el enlace desde el teléfono. También puedes servirla en tu red local:

```bash
python -m http.server 4173
```

y entrar desde el celular a `http://TU-IP:4173`.

## Qué incluye

- **Setlist en orden** con las 18 posiciones del show de Puebla y CDMX.
- **Bloques con varias letras**: las posiciones 12 (tres canciones), 13 (dos canciones) y 14 (dos canciones) muestran pestañas para guardar y consultar cada letra por separado sin agregar filas al setlist.
- **Buscador y filtros**: todas, con letra, sin letra, para repasar y listas.
- **Estado por canción**: toca el punto de la derecha para alternar entre *Por ver → Repasar → Lista*. El anillo de la barra superior muestra el avance.
- **Letras visibles y editables** con guardado automático en el navegador (`localStorage`). Al abrir una canción verás la letra; toca **Editar letra** para modificarla y **Listo ✓** para volver a la vista de lectura. Nada se sube a internet.
- **Botón Pegar** para traer la letra desde el portapapeles y **Buscar letra** para abrir una búsqueda.
- **Modo concierto** a pantalla completa: letra grande, navegación con botones, flechas del teclado o deslizando el dedo, y bloqueo de pantalla si el navegador lo permite.
- **Versión móvil instalable**: se adapta al celular, se puede agregar a la pantalla de inicio y funciona sin conexión una vez cargada.
- **Playlist de Spotify** embebida y enlace directo.
- **Respaldo**: exporta un `.json` con tus letras y estados, e impórtalo en otro dispositivo.
- Diseño adaptable a celular, tablet y escritorio.

## Instalarla en el celular

Si ya está publicada en GitHub Pages:

1. Abre `https://08nicks.github.io/mcaese_songs/` en Chrome o Safari desde el teléfono.
2. **iPhone:** toca Compartir → **Agregar a pantalla de inicio**. **Android:** abre el menú → **Instalar app**.
3. Se abrirá a pantalla completa como una app y funcionará sin conexión después de la primera carga.

Las letras siguen guardándose en ese dispositivo. Para pasarlas desde la computadora, usa **Exportar respaldo** e **Importar**.

## Cómo agregar las letras

1. Toca una canción del setlist. Si la posición tiene un bloque con varias canciones, elige la pestaña de la que quieres editar.
2. Toca **Editar letra** y pega la letra en el campo de texto (puedes usar el botón **Pegar** o mantener pulsado y elegir *Pegar*).
3. Toca **Listo ✓**. Se guarda sola en tu dispositivo y vuelve a la vista de lectura.

> Las letras no vienen incluidas en el código por derechos de autor. La página funciona como tu bloc de notas personal: tú agregas tu copia y se queda únicamente en tu dispositivo.

## Personalizar el setlist o la fecha

Todo está en `songs.js`:

- `date`: fecha y hora del concierto (formato ISO con zona horaria).
- `songs`: arreglo con cada canción. Puedes cambiar el orden, agregar o quitar canciones, o incluir `lyrics` por defecto.
- `parts`: para bloques con varias canciones. Cada parte lleva `id`, `title` y opcionalmente `lyrics`, y aparece como una pestaña dentro de la misma posición.
- `note`: etiqueta extra, por ejemplo `"Pendiente"`, `"Mitad"` o `"2 rolas"`.

Si agregas una canción nueva, usa un `id` único (sin espacios ni acentos).

## Publicarla gratis

### GitHub Pages

1. En el repositorio, entra a **Settings → Pages**.
2. En *Build and deployment*, elige **Deploy from a branch**.
3. Selecciona la rama **main** y la carpeta **/ (root)**. Guarda.
4. En unos minutos quedará disponible en `https://08nicks.github.io/mcaese_songs/`.

### Netlify

1. Entra a [Netlify Drop](https://app.netlify.com/drop).
2. Arrastra la carpeta completa del proyecto.
3. Te dará un enlace HTTPS listo para abrir en el celular.

También funciona en Vercel sin cambiar nada.

## Notas

- El reproductor de Spotify y las tipografías necesitan internet. El setlist, tus letras y el modo concierto funcionan sin conexión una vez cargada la página.
- El botón **Pegar** usa la API del portapapeles; si el navegador no lo permite (por ejemplo al abrir el archivo con `file://`), pega manualmente con una pulsación larga.
- Los datos viven en el navegador de ese dispositivo. Si cambias de celular o borras los datos del navegador, usa **Exportar respaldo** antes.
