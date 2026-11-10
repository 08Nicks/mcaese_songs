"""
Servidor local para la app y el karaoke.

`python -m http.server` no soporta peticiones Range, por lo que el audio se
traba o se reinicia al buscar dentro de la canción. Este servidor sí las
soporta y atiende varias conexiones a la vez.

Uso:
    python serve.py            # http://127.0.0.1:4173
    python serve.py 8000       # otro puerto
"""

from __future__ import annotations

import os
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        if not os.path.isfile(path):
            self.send_error(404, "File not found")
            return None

        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        size = os.fstat(f.fileno()).st_size
        start, end = 0, size - 1
        status = 200

        header = self.headers.get("Range")
        if header:
            match = RANGE_RE.fullmatch(header.strip())
            if match:
                first, last = match.groups()
                if first:
                    start = int(first)
                    end = int(last) if last else size - 1
                elif last:
                    # bytes=-N: últimos N bytes.
                    start = max(0, size - int(last))
                end = min(end, size - 1)
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.end_headers()
                    f.close()
                    return None
                status = 206

        self.send_response(status)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        if status == 206:
            f.seek(start)
            remaining = end - start + 1

            class Limited:
                def __init__(self, fileobj, limit):
                    self.fileobj = fileobj
                    self.limit = limit

                def read(self, n=-1):
                    if self.limit <= 0:
                        return b""
                    if n is None or n < 0 or n > self.limit:
                        n = self.limit
                    data = self.fileobj.read(n)
                    self.limit -= len(data)
                    return data

                def close(self):
                    self.fileobj.close()

            return Limited(f, remaining)
        return f

    def log_message(self, fmt, *args):
        # Menos ruido en la consola.
        pass

    def handle_error(self, request, client_address):
        # El navegador corta las peticiones de audio a propósito; no es un error.
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError)):
            return
        super().handle_error(request, client_address)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
    handler = partial(Handler, directory=ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Servidor en http://127.0.0.1:{port}")
    print(f"Carpeta: {ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
